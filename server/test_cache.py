"""
Test script to verify draft caching functionality.

This script tests:
1. Cache miss on first generation
2. Cache hit on second generation
3. Cache invalidation
4. Cache statistics
"""

import asyncio
import sys
from datetime import datetime

# Add server to path
sys.path.insert(0, '.')

from app.database import db, client
from app.ai.draft_cache_service import draft_cache_service


async def test_caching():
    """Test the draft caching functionality."""
    print("=" * 60)
    print("DRAFT CACHING TEST SUITE")
    print("=" * 60)
    
    # Test data
    test_user = "test_user_123"
    test_email_id = "email_001"
    test_response = "This is a test generated response."
    test_profile = {
        "verbosity": 0.7,
        "politeness": 0.8,
        "professionalism": 0.9
    }
    
    try:
        # Clean up any existing test data
        print("\n1. Cleaning up old test data...")
        await db.response_drafts.delete_many({
            "user_id": test_user
        })
        print("   ✓ Cleanup complete")
        
        # Test 1: Save draft
        print("\n2. Testing save_draft()...")
        draft_id = await draft_cache_service.save_draft(
            user_id=test_user,
            email_id=test_email_id,
            email_subject="Test Subject",
            email_body="This is a test email body",
            sender="test@example.com",
            generated_response=test_response,
            profile_snapshot=test_profile,
            temperature=0.7,
            max_tokens=300
        )
        print(f"   ✓ Draft saved with ID: {draft_id}")
        
        # Test 2: Retrieve cached draft
        print("\n3. Testing get_cached_draft() - Should hit cache...")
        cached = await draft_cache_service.get_cached_draft(test_user, test_email_id)
        if cached:
            print(f"   ✓ Cache hit! Retrieved: {cached['generated_response']}")
            print(f"   ✓ Cache status: {cached['status']}")
            print(f"   ✓ Expires at: {cached['expires_at']}")
        else:
            print("   ✗ Cache miss (unexpected)")
            return False
        
        # Test 3: Cache miss for different email
        print("\n4. Testing get_cached_draft() for different email...")
        different_cached = await draft_cache_service.get_cached_draft(test_user, "email_999")
        if different_cached is None:
            print("   ✓ Correctly returned None for uncached email")
        else:
            print("   ✗ Incorrectly returned cached value")
            return False
        
        # Test 4: Cache statistics
        print("\n5. Testing get_cache_stats()...")
        stats = await draft_cache_service.get_cache_stats(test_user)
        print(f"   ✓ Active drafts: {stats['active_drafts']}")
        print(f"   ✓ Expired drafts: {stats['expired_drafts']}")
        print(f"   ✓ Total accesses: {stats['total_accesses']}")
        
        # Test 5: Invalidate draft
        print("\n6. Testing invalidate_draft()...")
        invalidated = await draft_cache_service.invalidate_draft(test_user, test_email_id)
        if invalidated:
            print("   ✓ Draft invalidated successfully")
        else:
            print("   ✗ Failed to invalidate draft")
            return False
        
        # Test 6: Verify invalidated draft returns None
        print("\n7. Verifying invalidated draft is not cached...")
        invalidated_cached = await draft_cache_service.get_cached_draft(test_user, test_email_id)
        if invalidated_cached is None:
            print("   ✓ Invalidated draft correctly returns None")
        else:
            print("   ✗ Invalidated draft still returned (unexpected)")
            return False
        
        # Test 7: Save new draft and verify fresh stats
        print("\n8. Testing cache updates after invalidation...")
        await draft_cache_service.save_draft(
            user_id=test_user,
            email_id=test_email_id,
            email_subject="Test Subject 2",
            email_body="Updated test email body",
            sender="test2@example.com",
            generated_response="Updated response",
            profile_snapshot=test_profile,
            temperature=0.7,
            max_tokens=300
        )
        stats = await draft_cache_service.get_cache_stats(test_user)
        print(f"   ✓ Active drafts after re-save: {stats['active_drafts']}")
        
        # Clean up
        print("\n9. Cleaning up test data...")
        await db.response_drafts.delete_many({
            "user_id": test_user
        })
        print("   ✓ Cleanup complete")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Close database connection
        client.close()


if __name__ == "__main__":
    result = asyncio.run(test_caching())
    sys.exit(0 if result else 1)
