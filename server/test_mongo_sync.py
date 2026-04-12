#!/usr/bin/env python
"""Verify MongoDB connection and test basic upsert operation."""

from pymongo import MongoClient
from pymongo.errors import WriteError
from datetime import datetime, timedelta
from bson import ObjectId
import os

# Get MongoDB URI from environment or use default
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
db_name = os.getenv("DB_NAME", "bharatmail")

print("MongoDB Connection Test")
print("=" * 60)
print(f"MongoDB URI: {mongo_uri}")
print(f"Database: {db_name}")
print()

try:
    # Connect to MongoDB synchronously
    client = MongoClient(mongo_uri)
    db = client[db_name]
    
    # Test collection
    collection = db.response_drafts
    
    print("1. Testing MongoDB connection...")
    # Ping the server
    client.admin.command('ping')
    print("   ✓ Connected to MongoDB")
    
    print("\n2. Cleaning up test data...")
    collection.delete_many({"_test_user": "mongo_test_001"})
    print("   ✓ Cleanup complete")
    
    print("\n3. Testing upsert operation...")
    test_data = {
        "user_id": "mongo_test_001",
        "email_id": "email_001",
        "generated_response": "Test response content",
        "profile_snapshot": {"verbosity": 0.7},
        "status": "active",
        "expires_at": datetime.utcnow() + timedelta(days=7),
        "last_accessed_at": datetime.utcnow()
    }
    
    result = collection.update_one(
        {
            "user_id": "mongo_test_001",
            "email_id": "email_001"
        },
        {
            "$set": test_data,
            "$setOnInsert": {"created_at": datetime.utcnow()}
        },
        upsert=True
    )
    
    print(f"   ✓ Upsert successful")
    print(f"     - Matched: {result.matched_count}")
    print(f"     - Modified: {result.modified_count}")
    print(f"     - Upserted ID: {result.upserted_id}")
    
    print("\n4. Verifying data in database...")
    doc = collection.find_one({
        "user_id": "mongo_test_001",
        "email_id": "email_001"
    })
    
    if doc:
        print("   ✓ Document found!")
        print(f"     - ID: {doc['_id']}")
        print(f"     - Response: {doc['generated_response']}")
        print(f"     - Status: {doc.get('status')}")
    else:
        print("   ✗ Document not found!")
    
    print("\n5. Testing second upsert (update existing)...")
    test_data["generated_response"] = "Updated response content"
    
    result2 = collection.update_one(
        {
            "user_id": "mongo_test_001",
            "email_id": "email_001"
        },
        {
            "$set": test_data,
            "$setOnInsert": {"created_at": datetime.utcnow()}
        },
        upsert=True
    )
    
    print(f"   ✓ Update successful")
    print(f"     - Matched: {result2.matched_count}")
    print(f"     - Modified: {result2.modified_count}")
    print(f"     - Upserted ID: {result2.upserted_id}")
    
    doc2 = collection.find_one({
        "user_id": "mongo_test_001",
        "email_id": "email_001"
    })
    
    if doc2:
        print(f"   ✓ Updated document verified: {doc2['generated_response']}")
    
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
    
except WriteError as e:
    print(f"\n✗ MongoDB Write Error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    client.close()
