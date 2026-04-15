from motor.motor_asyncio import AsyncIOMotorClient
from .config import MONGO_URI, DB_NAME
import pymongo

client = AsyncIOMotorClient(MONGO_URI)
db = client[DB_NAME]

async def init_indexes():
    await db.users.create_index("username", unique=True)

    await db.messages.create_index(
        [("recipients", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)]
    )

    await db.messages.create_index(
        [("sender", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)]
    )

    await db.messages.create_index(
        [("subject", "text"), ("body", "text")]
    )

    # 🔥 NEW: Per-User Priority Queue Index
    await db.messages.create_index(
        [
            ("recipients", pymongo.ASCENDING),
            ("queue_status", pymongo.ASCENDING),
            ("queue_priority", pymongo.ASCENDING),
            ("created_at", pymongo.ASCENDING),
        ]
    )
    # Add inside init_indexes()

    # Calendar Suggestions Index
    await db.event_suggestions.create_index(
        [
            ("owner", pymongo.ASCENDING),
            ("status", pymongo.ASCENDING),
            ("created_at", pymongo.DESCENDING),
        ]
    )

    # Calendar Events Index
    await db.events.create_index(
        [
            ("owner", pymongo.ASCENDING),
            ("event_time", pymongo.ASCENDING),
        ]
    )
    await db.event_suggestions.create_index(
    [("owner", 1), ("message_id", 1)],
    unique=True
    )

    # ========== AI Response Generation Indexes ==========

    # User profiles index
    await db.user_profiles.create_index("user_id", unique=True)

    # Response history indexes
    await db.response_history.create_index(
        [("user_id", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)]
    )
    await db.response_history.create_index(
        [("user_id", pymongo.ASCENDING), ("original_email_id", pymongo.ASCENDING)]
    )

    # Training queue index
    await db.training_queue.create_index(
        [("user_id", pymongo.ASCENDING), ("status", pymongo.ASCENDING), ("created_at", pymongo.ASCENDING)]
    )

    # Response drafts indexes (for queue and cache lookups)
    # Drop old indexes to avoid conflicts
    try:
        await db.response_drafts.drop_index("user_id_1_message_id_1")
    except:
        pass  # Index doesn't exist, that's fine
    
    try:
        await db.response_drafts.drop_index("user_id_1_email_id_1")
    except:
        pass  # Index doesn't exist, that's fine
    
    try:
        await db.response_drafts.drop_index("message_id_1")
    except:
        pass  # Index doesn't exist, that's fine
    
    # PRIMARY: Unique sparse index on (user_id, email_id) for direct cache lookups
    # Sparse allows multiple null values (for queue-based drafts without email_id)
    await db.response_drafts.create_index(
        [("user_id", pymongo.ASCENDING), ("email_id", pymongo.ASCENDING)],
        unique=True,
        sparse=True  # Allow multiple null values
    )
    
    # SECONDARY: Non-unique index on message_id for queue processor lookups
    # (message_id may be null for new emails not yet synced to messages collection)
    await db.response_drafts.create_index(
        [("user_id", pymongo.ASCENDING), ("message_id", pymongo.ASCENDING)],
        sparse=True  # Sparse to allow multiple nulls
    )
    
    # Status and user lookup
    await db.response_drafts.create_index(
        [("user_id", pymongo.ASCENDING), ("status", pymongo.ASCENDING)]
    )
    
    # TTL index for automatic cleanup
    await db.response_drafts.create_index(
        [("expires_at", pymongo.ASCENDING)],
        expireAfterSeconds=0
    )