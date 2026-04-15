"""
Fix E11000 duplicate key error by dropping and recreating the unique index.
This makes the index SPARSE so it allows multiple null values.
"""

import asyncio
import pymongo
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI, DB_NAME


async def fix_indexes():
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    print("🔧 Fixing response_drafts indexes...")
    
    try:
        # Drop the problematic non-sparse unique index
        print("  → Dropping old non-sparse index...")
        await db.response_drafts.drop_index("user_id_1_email_id_1")
        print("    ✓ Old index dropped")
    except Exception as e:
        print(f"    ℹ️  Index doesn't exist yet: {e}")
    
    try:
        # Delete documents with email_id: null to clean up
        print("  → Cleaning up documents with email_id=null...")
        result = await db.response_drafts.delete_many({"email_id": None})
        print(f"    ✓ Deleted {result.deleted_count} documents with null email_id")
    except Exception as e:
        print(f"    ⚠️  Failed to clean up: {e}")
    
    # Create the new sparse unique index
    print("  → Creating new SPARSE unique index...")
    try:
        await db.response_drafts.create_index(
            [("user_id", pymongo.ASCENDING), ("email_id", pymongo.ASCENDING)],
            unique=True,
            sparse=True  # This allows multiple null values
        )
        print("    ✓ Sparse unique index created successfully!")
    except Exception as e:
        print(f"    ✗ Error creating index: {e}")
        return False
    
    print("\n✅ Index fix complete! You can now generate responses from the queue.")
    await client.close()
    return True


if __name__ == "__main__":
    success = asyncio.run(fix_indexes())
    exit(0 if success else 1)
