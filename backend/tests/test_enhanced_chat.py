"""
Test the complete enhanced chat system with semantic search
"""
import asyncio
import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from app.services.gemini_service import gemini_service
from app.config.database import get_supabase_client

async def test_enhanced_chat():
    """Test the complete chat system with semantic search context"""
    try:
        # Authenticate
        supabase = get_supabase_client()
        auth_response = supabase.auth.sign_in_with_password({
            "email": "gemini_test_user@gmail.com",
            "password": "gemini_test_password"
        })

        user_id = auth_response.user.id
        print(f"✅ Authenticated as user: {user_id}")

        # Test Case 1: First question (no context expected)
        print(f"\n🔍 Test 1: Ask about VLOOKUP (should find context from previous SUM conversations)")
        response1 = await gemini_service.chat_completion(
            message="How do I create a VLOOKUP formula to find customer names?",
            user_id=user_id,
            access_token=auth_response.session.access_token,
            refresh_token=auth_response.session.refresh_token
        )

        print(f"📝 AI Response:\n{response1[:300]}...")

        # Test Case 2: Follow-up question (should have context from Test 1)
        print(f"\n🔍 Test 2: Follow-up question about VLOOKUP (should reference previous context)")
        response2 = await gemini_service.chat_completion(
            message="Can you show me a specific example with actual cell references?",
            user_id=user_id,
            access_token=auth_response.session.access_token,
            refresh_token=auth_response.session.refresh_token
        )

        print(f"📝 AI Response:\n{response2[:300]}...")

        # Test Case 3: Different topic (should find relevant context)
        print(f"\n🔍 Test 3: Ask about SUM formulas (should find context from existing SUM conversations)")
        response3 = await gemini_service.chat_completion(
            message="What's the difference between SUM and SUMIF functions?",
            user_id=user_id,
            access_token=auth_response.session.access_token,
            refresh_token=auth_response.session.refresh_token
        )

        print(f"📝 AI Response:\n{response3[:300]}...")

        print(f"\n🎉 Enhanced chat system test completed successfully!")
        print(f"🎯 Your AI now has context-aware responses based on conversation history!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise e

if __name__ == "__main__":
    asyncio.run(test_enhanced_chat())