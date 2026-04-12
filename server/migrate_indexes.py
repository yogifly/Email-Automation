#!/usr/bin/env python
"""
Database Index Migration Script
Removes the old problematic unique index and recreates proper sparse indexes.
Run this once to fix the E11000 duplicate key error.
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import MONGO_URI, DB_NAME
import pymongo

async def migrate_indexes():
    """Fix response_drafts indexes."""
    
    client = AsyncIOMotorClient(MONGO_URI)
    db = client[DB_NAME]
    
    try:
        print("🔄 Starting index migration...")
        print(f"📦 Database: {DB_NAME}")
        
        # Get current indexes
        print("\n📋 Current indexes on response_drafts:")
        indexes = await db.response_drafts.list_indexes().to_list(None)
        for idx in indexes:
            print(f"  - {idx['name']}: {idx['key']}")
        
        # Remove bad indexes (they will be recreated as sparse)
        print("\n🗑️  Removing old indexes...")
        try:
            await db.response_drafts.drop_index("user_id_1_email_id_1")
            print("  ✓ Dropped user_id_1_email_id_1 (will recreate as SPARSE)")
        except Exception as e:
            print(f"  ℹ️  user_id_1_email_id_1 not found (OK): {e}")
        
        try:
            await db.response_drafts.drop_index("user_id_1_message_id_1")
            print("  ✓ Dropped user_id_1_message_id_1 (will recreate as SPARSE)")
        except Exception as e:
            print(f"  ℹ️  user_id_1_message_id_1 not found (OK): {e}")
        
        # Create new sparse indexes
        print("\n✨ Creating new SPARSE indexes...")
        
        # Unique index on (user_id, message_id) - SPARSE allows null values
        await db.response_drafts.create_index(
            [("user_id", pymongo.ASCENDING), ("message_id", pymongo.ASCENDING)],
            unique=True,
            sparse=True,
            name="user_id_1_message_id_1_sparse"
        )
        print("  ✓ Created (user_id, message_id) - SPARSE UNIQUE")
        
        # Unique index on (user_id, email_id) - SPARSE allows null values
        await db.response_drafts.create_index(
            [("user_id", pymongo.ASCENDING), ("email_id", pymongo.ASCENDING)],
            unique=True,
            sparse=True,
            name="user_id_1_email_id_1_sparse"
        )
        print("  ✓ Created (user_id, email_id) - SPARSE UNIQUE")
        
        # Status lookup index
        await db.response_drafts.create_index(
            [("user_id", pymongo.ASCENDING), ("status", pymongo.ASCENDING)],
            name="user_id_1_status_1"
        )
        print("  ✓ Created (user_id, status) - Regular index")
        
        # TTL index
        await db.response_drafts.create_index(
            [("expires_at", pymongo.ASCENDING)],
            expireAfterSeconds=0,
            name="expires_at_1_ttl"
        )
        print("  ✓ Created TTL index on expires_at")
        
        # List final indexes
        print("\n📋 Final indexes on response_drafts:")
        indexes = await db.response_drafts.list_indexes().to_list(None)
        for idx in indexes:
            print(f"  - {idx['name']}: {idx['key']}")
        
        print("\n✅ Index migration complete!")
        print("\n📝 What was fixed:")
        print("  1. Old non-sparse UNIQUE indexes removed")
        print("  2. New SPARSE UNIQUE indexes created")
        print("  3. SPARSE indexes allow null values without duplicate key errors")
        print("  4. Can now handle multiple null message_id values per user")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(migrate_indexes())
    print("\n💾 Done!")
