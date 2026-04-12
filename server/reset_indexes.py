#!/usr/bin/env python3
"""
Reset MongoDB indexes for response_drafts collection.
Removes the problematic UNIQUE constraint on message_id and recreates correct indexes.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI, DB_NAME
import pymongo

async def reset_indexes():
    """Reset the response_drafts collection indexes."""
    print("🔧 Resetting response_drafts indexes...")
    
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    try:
        # List all current indexes
        print("\n📋 Current indexes:")
        indexes = await db.response_drafts.list_indexes().to_list(None)
        for idx in indexes:
            print(f"  - {idx['name']}: {idx['key']}")
        
        # Drop problematic indexes
        print("\n🗑️  Dropping old indexes...")
        
        index_names = ["user_id_1_message_id_1", "user_id_1_email_id_1", "message_id_1"]
        for idx_name in index_names:
            try:
                await db.response_drafts.drop_index(idx_name)
                print(f"  ✓ Dropped: {idx_name}")
            except Exception as e:
                print(f"  ⊘ Skip: {idx_name} ({str(e)[:50]}...)")
        
        # Create new correct indexes
        print("\n✨ Creating new indexes...")
        
        # PRIMARY: Unique on (user_id, email_id)
        await db.response_drafts.create_index(
            [("user_id", pymongo.ASCENDING), ("email_id", pymongo.ASCENDING)],
            unique=True
        )
        print("  ✓ Created unique index: user_id_1_email_id_1")
        
        # SECONDARY: Non-unique sparse on (user_id, message_id)
        await db.response_drafts.create_index(
            [("user_id", pymongo.ASCENDING), ("message_id", pymongo.ASCENDING)],
            sparse=True
        )
        print("  ✓ Created sparse index: user_id_1_message_id_1")
        
        # Status lookup
        await db.response_drafts.create_index(
            [("user_id", pymongo.ASCENDING), ("status", pymongo.ASCENDING)]
        )
        print("  ✓ Created index: user_id_1_status_1")
        
        # TTL
        await db.response_drafts.create_index(
            [("expires_at", pymongo.ASCENDING)],
            expireAfterSeconds=0
        )
        print("  ✓ Created TTL index: expires_at_1")
        
        # List final indexes
        print("\n📋 Final indexes:")
        indexes = await db.response_drafts.list_indexes().to_list(None)
        for idx in indexes:
            print(f"  - {idx['name']}: {idx['key']}")
        
        print("\n✅ Index reset complete!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(reset_indexes())
