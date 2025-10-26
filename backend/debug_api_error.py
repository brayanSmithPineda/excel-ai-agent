#!/usr/bin/env python3
"""
Debug script to find the exact location of the 'NoneType' error in API endpoint
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.gemini_service import GeminiService

async def test_api_flow():
    """Test the exact API flow to find the error"""
    print("=== DEBUGGING: API Flow Error Location ===")
    print("=" * 60)
    
    try:
        # Initialize service
        service = GeminiService()
        print("GeminiService initialized")
        
        # Test message that should trigger function calling
        test_message = "Execute Python code to calculate 2+2"
        print(f"Test message: '{test_message}'")
        
        print("\nSTEP 1: Testing with conversation_id=None (new conversation)...")
        print("-" * 50)
        
        # Test with None conversation_id (new conversation)
        result = await service.chat_completion(
            message=test_message, 
            conversation_id=None, 
            user_id='3fdc19ef-75eb-460b-a9b1-ebc5b5b8436b'
        )
        
        print(f"Result with None conversation_id:")
        print(f"   - Executed code: {result.get('executed_code', 'N/A')}")
        print(f"   - Conversation ID: {result.get('conversation_id', 'N/A')}")
        
        print("\nSTEP 2: Testing with existing conversation_id...")
        print("-" * 50)
        
        # Test with existing conversation_id
        existing_conversation_id = result.get('conversation_id')
        if existing_conversation_id:
            result2 = await service.chat_completion(
                message="Calculate 3+3", 
                conversation_id=existing_conversation_id, 
                user_id='3fdc19ef-75eb-460b-a9b1-ebc5b5b8436b'
            )
            
            print(f"Result with existing conversation_id:")
            print(f"   - Executed code: {result2.get('executed_code', 'N/A')}")
            print(f"   - Conversation ID: {result2.get('conversation_id', 'N/A')}")
        else:
            print("No conversation ID returned from first call")
        
        print("\n" + "=" * 60)
        print("DEBUGGING COMPLETE")
        
    except Exception as e:
        print(f"Error during debugging: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api_flow())
