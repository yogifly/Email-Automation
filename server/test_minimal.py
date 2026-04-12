#!/usr/bin/env python
"""Minimal test to verify save_draft works without MongoDB conflict."""

import asyncio
import sys
sys.path.insert(0, '.')

from app.database import db, client
from app.ai.draft_cache_service import draft_cache_service


async def test_save_draft():
    """Test the basic save_draft operation."""
    test_user = "test_user_simple"
    test_email_id = "email_minimal_001"
    
    try:
        # Clean up
        await db.response_drafts.delete_many({"user_id": test_user})
        
        # Test save_draft
        print("Testing save_draft()...")
        draft_id = await draft_cache_service.save_draft(
            user_id=test_user,
            email_id=test_email_id,
            email_subject="Test Subject",
            email_body="Test body",
            sender="test@example.com",
            generated_response="Test response",
            profile_snapshot={"verbosity": 0.7},
            temperature=0.7,
            max_tokens=300
        )
        
        print(f"✓ Draft saved with ID: {draft_id}")
        
        # Verify it exists
        draft = await db.response_drafts.find_one({"_id": draft_id})
        if draft:
            print(f"✓ Draft verified in database")
            print(f"  - Email ID: {draft['email_id']}")
            print(f"  - Response: {draft['generated_response'][:30]}...")
            return True
        else:
            print("✗ Draft not found after save")
            return False
            
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await client.close()


if __name__ == "__main__":
    success = asyncio.run(test_save_draft())
    sys.exit(0 if success else 1)
