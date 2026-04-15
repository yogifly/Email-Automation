"""
Draft Cache Service
Handles caching and retrieval of generated AI responses to avoid redundant regeneration.

When a user reloads the page, instead of regenerating the response again,
we fetch it from cache if it exists.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId

from app.database import db


class DraftCacheService:
    """
    Service for managing draft response cache.
    
    Stores generated responses keyed by (user_id, email_id) to enable
    quick retrieval without re-invoking the LLM.
    """
    
    # Default cache TTL: 7 days (can be overridden per request)
    DEFAULT_CACHE_TTL_DAYS = 7
    
    async def get_cached_draft(
        self,
        user_id: str,
        email_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached draft for a specific email.
        
        Args:
            user_id: Current user's ID
            email_id: ID of the original email
            
        Returns:
            Draft document if found and not expired, None otherwise
        """
        # Skip cache lookup if email_id is None (queue-based drafts)
        if not email_id:
            return None
            
        draft = await db.response_drafts.find_one({
            "user_id": user_id,
            "email_id": email_id,
            "status": "active"
        })
        
        if not draft:
            return None
        
        # Check if cache has expired
        if draft.get("expires_at") and draft["expires_at"] < datetime.utcnow():
            # Mark as expired
            await db.response_drafts.update_one(
                {"_id": draft["_id"]},
                {"$set": {"status": "expired"}}
            )
            return None
        
        return draft
    
    async def save_draft(
        self,
        user_id: str,
        email_id: str,
        email_subject: str,
        email_body: str,
        sender: str,
        generated_response: str,
        profile_snapshot: Dict[str, float],
        temperature: float = 0.7,
        max_tokens: int = 300,
        ttl_days: int = None
    ) -> str:
        """
        Cache a generated response draft.
        
        Args:
            user_id: Current user's ID
            email_id: ID of the original email (can be None for queue-based responses)
            email_subject: Subject of original email
            email_body: Body of original email
            sender: Sender of original email
            generated_response: AI-generated response text
            profile_snapshot: User profile used for generation
            temperature: Generation temperature used
            max_tokens: Max tokens used
            ttl_days: Cache TTL in days (None = use default)
            
        Returns:
            Draft ID (string)
        """
        ttl = ttl_days or self.DEFAULT_CACHE_TTL_DAYS
        expires_at = datetime.utcnow() + timedelta(days=ttl)
        
        # Prepare the update data
        update_data = {
            "user_id": user_id,
            "email_id": email_id,
            "email_subject": email_subject,
            "email_body": email_body,
            "sender": sender,
            "generated_response": generated_response,
            "profile_snapshot": profile_snapshot,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "status": "active",
            "expires_at": expires_at,
            "last_accessed_at": datetime.utcnow()
        }
        
        # Skip upsert if email_id is None (queue-based drafts are managed separately)
        if not email_id:
            return ""  # Queue drafts don't use cache storage
        
        # Simple upsert for inbox-based drafts
        result = await db.response_drafts.update_one(
            {
                "user_id": user_id,
                "email_id": email_id
            },
            {
                "$set": update_data,
                "$setOnInsert": {"created_at": datetime.utcnow()}
            },
            upsert=True
        )
        
        # If it was an insert, get the ID from the result
        if result.upserted_id:
            return str(result.upserted_id)
        
        # If it was an update, find and return the ID
        draft = await db.response_drafts.find_one({
            "user_id": user_id,
            "email_id": email_id
        })
        return str(draft["_id"]) if draft else ""
    
    async def invalidate_draft(
        self,
        user_id: str,
        email_id: str
    ) -> bool:
        """
        Invalidate a cached draft (mark as expired).
        
        Args:
            user_id: Current user's ID
            email_id: Email ID to invalidate cache for
            
        Returns:
            True if a draft was found and invalidated, False otherwise
        """
        result = await db.response_drafts.update_one(
            {
                "user_id": user_id,
                "email_id": email_id,
                "status": "active"
            },
            {
                "$set": {
                    "status": "invalidated",
                    "invalidated_at": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0
    
    async def cleanup_expired_drafts(self) -> int:
        """
        Delete expired drafts from database.
        Run periodically to clean up old cache entries.
        
        Returns:
            Number of drafts deleted
        """
        result = await db.response_drafts.delete_many({
            "status": "expired",
            "expires_at": {"$lt": datetime.utcnow()}
        })
        
        return result.deleted_count
    
    async def get_cache_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Get cache statistics for a user.
        
        Args:
            user_id: Current user's ID
            
        Returns:
            Dictionary with cache stats
        """
        active_drafts = await db.response_drafts.count_documents({
            "user_id": user_id,
            "status": "active"
        })
        
        expired_drafts = await db.response_drafts.count_documents({
            "user_id": user_id,
            "status": "expired"
        })
        
        total_accesses = await db.response_drafts.aggregate([
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": None, "total": {"$sum": "$access_count"}}}
        ]).to_list(None)
        
        return {
            "active_drafts": active_drafts,
            "expired_drafts": expired_drafts,
            "total_accesses": total_accesses[0]["total"] if total_accesses else 0
        }


# Singleton instance
draft_cache_service = DraftCacheService()
