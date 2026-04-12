"""
User Profile Service
Manages user communication style profiles for personalized response generation.

Profile structure:
- verbosity: 0-1 (avg sentence length normalized)
- politeness: 0-1 (courtesy words frequency)  
- professionalism: 0-1 (formality score)
"""

import re
from datetime import datetime
from typing import Optional, Dict, List
from dataclasses import dataclass, asdict
from app.database import db


@dataclass
class UserProfile:
    """User communication style profile."""
    user_id: str
    verbosity: float = 0.5          # 0=terse, 1=verbose
    politeness: float = 0.5         # 0=direct, 1=very polite
    professionalism: float = 0.5    # 0=casual, 1=formal
    avg_response_length: int = 100  # average word count
    interaction_count: int = 0
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        d = asdict(self)
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "UserProfile":
        return cls(
            user_id=data["user_id"],
            verbosity=data.get("verbosity", 0.5),
            politeness=data.get("politeness", 0.5),
            professionalism=data.get("professionalism", 0.5),
            avg_response_length=data.get("avg_response_length", 100),
            interaction_count=data.get("interaction_count", 0),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )

    def get_style_description(self) -> str:
        """Convert profile to natural language for prompt conditioning."""
        parts = []

        # Verbosity
        if self.verbosity < 0.33:
            parts.append("concise and brief")
        elif self.verbosity > 0.66:
            parts.append("detailed and thorough")
        else:
            parts.append("moderately detailed")

        # Politeness
        if self.politeness < 0.33:
            parts.append("direct")
        elif self.politeness > 0.66:
            parts.append("very polite and courteous")
        else:
            parts.append("polite")

        # Professionalism
        if self.professionalism < 0.33:
            parts.append("casual and friendly")
        elif self.professionalism > 0.66:
            parts.append("formal and professional")
        else:
            parts.append("semi-formal")

        return ", ".join(parts)


class TextAnalyzer:
    """Analyzes text to extract style features."""

    POLITE_WORDS = {
        "please", "thank", "thanks", "appreciate", "grateful", "kindly",
        "would you", "could you", "may i", "excuse me", "sorry", "pardon",
        "regards", "sincerely", "respectfully", "dear", "warm"
    }

    CASUAL_INDICATORS = {
        "hey", "hi", "yeah", "yep", "nope", "gonna", "wanna", "gotta",
        "cool", "awesome", "great", "ok", "okay", "btw", "fyi", "asap",
        "lol", "haha", "!", "..."
    }

    FORMAL_INDICATORS = {
        "therefore", "furthermore", "however", "consequently", "regarding",
        "pursuant", "accordingly", "hereby", "aforementioned", "undersigned",
        "per your request", "as discussed", "please find attached"
    }

    @classmethod
    def compute_verbosity(cls, text: str) -> float:
        """Compute verbosity score based on sentence length."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            return 0.5

        avg_words = sum(len(s.split()) for s in sentences) / len(sentences)

        # Normalize: 5 words = 0, 25+ words = 1
        normalized = min(1.0, max(0.0, (avg_words - 5) / 20))
        return round(normalized, 3)

    @classmethod
    def compute_politeness(cls, text: str) -> float:
        """Compute politeness score based on courtesy words."""
        text_lower = text.lower()
        word_count = len(text.split())

        if word_count == 0:
            return 0.5

        polite_count = sum(1 for word in cls.POLITE_WORDS if word in text_lower)

        # Normalize: 0 matches = 0, 5+ matches per 100 words = 1
        normalized = min(1.0, (polite_count / max(1, word_count / 100)) / 5)
        return round(normalized, 3)

    @classmethod
    def compute_professionalism(cls, text: str) -> float:
        """Compute professionalism score based on formality indicators."""
        text_lower = text.lower()

        formal_count = sum(1 for ind in cls.FORMAL_INDICATORS if ind in text_lower)
        casual_count = sum(1 for ind in cls.CASUAL_INDICATORS if ind in text_lower)

        # Base score
        score = 0.5

        # Adjust based on indicators
        score += formal_count * 0.1
        score -= casual_count * 0.08

        return round(min(1.0, max(0.0, score)), 3)

    @classmethod
    def analyze_text(cls, text: str) -> Dict[str, float]:
        """Analyze text and return all style metrics."""
        return {
            "verbosity": cls.compute_verbosity(text),
            "politeness": cls.compute_politeness(text),
            "professionalism": cls.compute_professionalism(text),
            "word_count": len(text.split())
        }


class UserProfileService:
    """Service for managing user profiles in MongoDB."""

    def __init__(self):
        self.collection = db.user_profiles
        self.analyzer = TextAnalyzer()

    async def get_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile from database."""
        doc = await self.collection.find_one({"user_id": user_id})
        if doc:
            return UserProfile.from_dict(doc)
        return None

    async def create_profile(self, user_id: str) -> UserProfile:
        """Create new profile with defaults, or return existing."""
        profile = UserProfile(user_id=user_id)
        try:
            await self.collection.insert_one(profile.to_dict())
        except Exception as e:
            # Handle duplicate key error - profile already exists
            if "duplicate key" in str(e).lower() or "E11000" in str(e):
                existing = await self.get_profile(user_id)
                if existing:
                    return existing
            raise
        return profile

    async def get_or_create_profile(self, user_id: str) -> UserProfile:
        """Get existing profile or create new one (race-condition safe)."""
        profile = await self.get_profile(user_id)
        if profile is not None:
            return profile
        
        # Use upsert to avoid race conditions
        default_profile = UserProfile(user_id=user_id)
        await self.collection.update_one(
            {"user_id": user_id},
            {"$setOnInsert": default_profile.to_dict()},
            upsert=True
        )
        
        # Fetch the actual profile (might have been created by another request)
        return await self.get_profile(user_id)

    async def update_profile(self, profile: UserProfile) -> None:
        """Update profile in database."""
        profile.updated_at = datetime.utcnow()
        await self.collection.update_one(
            {"user_id": profile.user_id},
            {"$set": profile.to_dict()},
            upsert=True
        )

    async def initialize_from_sent_emails(self, user_id: str) -> UserProfile:
        """
        Initialize user profile by analyzing their sent emails.
        Called for new users or to recalibrate profile.
        """
        # Get user's sent messages
        cursor = db.messages.find({"sender": user_id}).limit(50)

        texts = []
        async for msg in cursor:
            texts.append(f"{msg.get('subject', '')} {msg.get('body', '')}")

        if not texts:
            # No sent emails, return default profile
            return await self.get_or_create_profile(user_id)

        # Analyze all texts
        combined_metrics = {
            "verbosity": [],
            "politeness": [],
            "professionalism": [],
            "word_count": []
        }

        for text in texts:
            metrics = self.analyzer.analyze_text(text)
            for key, value in metrics.items():
                combined_metrics[key].append(value)

        # Average the metrics
        profile = await self.get_or_create_profile(user_id)
        profile.verbosity = round(sum(combined_metrics["verbosity"]) / len(texts), 3)
        profile.politeness = round(sum(combined_metrics["politeness"]) / len(texts), 3)
        profile.professionalism = round(sum(combined_metrics["professionalism"]) / len(texts), 3)
        profile.avg_response_length = int(sum(combined_metrics["word_count"]) / len(texts))

        await self.update_profile(profile)
        return profile

    async def incremental_update(
        self,
        user_id: str,
        generated_text: str,
        final_text: str,
        learning_rate: float = 0.1
    ) -> UserProfile:
        """
        Update profile based on difference between generated and user-edited response.
        Uses exponential moving average for smooth updates.
        """
        profile = await self.get_or_create_profile(user_id)

        # Analyze both texts
        gen_metrics = self.analyzer.analyze_text(generated_text)
        final_metrics = self.analyzer.analyze_text(final_text)

        # Compute deltas and apply EMA update
        profile.verbosity += learning_rate * (final_metrics["verbosity"] - gen_metrics["verbosity"])
        profile.politeness += learning_rate * (final_metrics["politeness"] - gen_metrics["politeness"])
        profile.professionalism += learning_rate * (final_metrics["professionalism"] - gen_metrics["professionalism"])

        # Update average response length
        profile.avg_response_length = int(
            profile.avg_response_length * (1 - learning_rate) +
            final_metrics["word_count"] * learning_rate
        )

        # Clamp values to [0, 1]
        profile.verbosity = round(min(1.0, max(0.0, profile.verbosity)), 3)
        profile.politeness = round(min(1.0, max(0.0, profile.politeness)), 3)
        profile.professionalism = round(min(1.0, max(0.0, profile.professionalism)), 3)

        # Increment interaction count
        profile.interaction_count += 1

        await self.update_profile(profile)
        return profile


# Singleton instance
profile_service = UserProfileService()
