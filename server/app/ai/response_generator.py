"""
Response Generator Service
Core service for generating personalized email responses.

Combines:
- Base LLM (Ollama/Mistral)
- User profile for style conditioning
- Prompt engineering for personalization
"""

from typing import Optional, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from bson import ObjectId

from app.database import db
from app.ai.user_profile import profile_service, UserProfile
from app.ai.ollama_client import ollama_client, OllamaError
from app.ai.draft_cache_service import draft_cache_service


@dataclass
class GenerationResult:
    """Result of response generation."""
    response_id: str
    generated_response: str
    profile_used: Dict[str, float]
    original_email_id: str
    generation_time_ms: int
    from_cache: bool = False


class ResponseGenerator:
    """
    Main service for generating personalized email responses.
    """

    # System prompt template for email response generation
    SYSTEM_PROMPT_TEMPLATE = """You are an AI assistant helping to compose email replies. 
Your task is to generate a reply to the given email.

Writing style guidelines:
- Be {style_description}
- Target response length: approximately {target_length} words
- Match the formality level of the original email when appropriate

Important:
- Only output the email reply body, no subject line
- Do not include "Subject:" or "Re:" prefixes
- Do not sign off with a name unless the context requires it
- Be helpful and address the content of the original email
"""

    USER_PROMPT_TEMPLATE = """Original Email:
From: {sender}
Subject: {subject}

{body}

---
Please write a reply to this email."""

    def __init__(self):
        self.profile_service = profile_service
        self.ollama = ollama_client
        self.cache = draft_cache_service

    async def generate_response(
        self,
        user_id: str,
        email_id: str,
        email_subject: str,
        email_body: str,
        sender: str,
        temperature: float = 0.7,
        max_tokens: int = 300,
        use_cache: bool = True,
        cache_ttl_days: int = None
    ) -> GenerationResult:
        """
        Generate a personalized email response with caching support.
        
        Args:
            user_id: Current user's ID
            email_id: ID of the email being replied to
            email_subject: Subject of original email
            email_body: Body of original email
            sender: Sender of original email
            temperature: Generation temperature
            max_tokens: Max tokens to generate
            use_cache: Whether to use cached response if available (default: True)
            cache_ttl_days: Cache time-to-live in days (default: 7)
            
        Returns:
            GenerationResult with generated response and metadata
        """
        start_time = datetime.utcnow()
        
        # Check cache first if enabled
        if use_cache:
            cached_draft = await self.cache.get_cached_draft(user_id, email_id)
            if cached_draft:
                # Return cached response with from_cache flag
                gen_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                return GenerationResult(
                    response_id=str(cached_draft["_id"]),
                    generated_response=cached_draft["generated_response"],
                    profile_used={
                        "verbosity": cached_draft["profile_snapshot"]["verbosity"],
                        "politeness": cached_draft["profile_snapshot"]["politeness"],
                        "professionalism": cached_draft["profile_snapshot"]["professionalism"]
                    },
                    original_email_id=email_id,
                    generation_time_ms=gen_time_ms,
                    from_cache=True
                )

        # Load or create user profile
        profile = await self.profile_service.get_or_create_profile(user_id)

        # If new user with no interaction history, try to initialize from sent emails
        if profile.interaction_count == 0:
            profile = await self.profile_service.initialize_from_sent_emails(user_id)

        # Build prompts
        system_prompt = self._build_system_prompt(profile)
        user_prompt = self._build_user_prompt(sender, email_subject, email_body)

        # Generate response using Ollama
        try:
            generated_text = await self.ollama.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except OllamaError as e:
            raise ResponseGenerationError(f"LLM generation failed: {str(e)}") from e

        # Clean up the generated response
        generated_text = self._clean_response(generated_text)

        # Calculate generation time
        end_time = datetime.utcnow()
        gen_time_ms = int((end_time - start_time).total_seconds() * 1000)

        # Store in response history
        response_doc = {
            "user_id": user_id,
            "original_email_id": email_id,
            "original_email_subject": email_subject,
            "original_email_body": email_body,
            "original_sender": sender,
            "generated_response": generated_text,
            "final_response": None,  # Will be filled when user submits
            "profile_snapshot": {
                "verbosity": profile.verbosity,
                "politeness": profile.politeness,
                "professionalism": profile.professionalism,
                "avg_response_length": profile.avg_response_length
            },
            "metrics": None,  # Will be computed after user edits
            "reward": None,
            "training_status": "pending",
            "created_at": datetime.utcnow(),
            "submitted_at": None
        }

        result = await db.response_history.insert_one(response_doc)
        response_id = str(result.inserted_id)
        
        # Cache the generated response for future reloads
        await self.cache.save_draft(
            user_id=user_id,
            email_id=email_id,
            email_subject=email_subject,
            email_body=email_body,
            sender=sender,
            generated_response=generated_text,
            profile_snapshot={
                "verbosity": profile.verbosity,
                "politeness": profile.politeness,
                "professionalism": profile.professionalism,
                "avg_response_length": profile.avg_response_length
            },
            temperature=temperature,
            max_tokens=max_tokens,
            ttl_days=cache_ttl_days
        )

        return GenerationResult(
            response_id=response_id,
            generated_response=generated_text,
            profile_used={
                "verbosity": profile.verbosity,
                "politeness": profile.politeness,
                "professionalism": profile.professionalism
            },
            original_email_id=email_id,
            generation_time_ms=gen_time_ms,
            from_cache=False
        )

    def _build_system_prompt(self, profile: UserProfile) -> str:
        """Build system prompt with profile-based style conditioning."""
        style_desc = profile.get_style_description()
        target_length = profile.avg_response_length

        return self.SYSTEM_PROMPT_TEMPLATE.format(
            style_description=style_desc,
            target_length=target_length
        )

    def _build_user_prompt(self, sender: str, subject: str, body: str) -> str:
        """Build user prompt with email details."""
        return self.USER_PROMPT_TEMPLATE.format(
            sender=sender,
            subject=subject or "(No subject)",
            body=body or "(Empty email body)"
        )

    def _clean_response(self, text: str) -> str:
        """Clean up generated response text."""
        text = text.strip()

        # Remove common unwanted prefixes
        prefixes_to_remove = [
            "Subject:", "Re:", "Reply:", "Response:",
            "Here's a reply:", "Here is a reply:",
            "Email reply:", "Dear", "Hi,"
        ]

        for prefix in prefixes_to_remove:
            if text.lower().startswith(prefix.lower()):
                text = text[len(prefix):].strip()

        # Remove surrounding quotes if present
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1].strip()

        return text

    async def get_response_history(
        self,
        user_id: str,
        limit: int = 20
    ) -> list:
        """Get user's response generation history."""
        cursor = db.response_history.find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(limit)

        results = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            doc.pop("_id", None)
            results.append(doc)

        return results

    async def get_response_by_id(
        self,
        response_id: str,
        user_id: str
    ) -> Optional[dict]:
        """Get a specific response record."""
        try:
            doc = await db.response_history.find_one({
                "_id": ObjectId(response_id),
                "user_id": user_id
            })
            if doc:
                doc["id"] = str(doc["_id"])
                doc.pop("_id", None)
                return doc
            return None
        except Exception:
            return None


class ResponseGenerationError(Exception):
    """Error during response generation."""
    pass


# Singleton instance
response_generator = ResponseGenerator()
