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