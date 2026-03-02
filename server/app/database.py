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