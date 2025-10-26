#!/usr/bin/env python3
"""
Debug script to test function calling implementation
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.gemini_service import GeminiService

async def test_function_calling():
    """Test the function calling implementation"""
    print("Testing function calling implementation...")
    
    try:
        # Initialize service
        service = GeminiService()
        print("GeminiService initialized")
        
        # Test with a simple calculation request
        print("Testing with: 'Calculate the sum of 1+1'")
        result = await service.chat_completion(
            message='Calculate the sum of 1+1', 
            conversation_id=None, 
            user_id='3fdc19ef-75eb-460b-a9b1-ebc5b5b8436b'
        )
        
        print("Function calling test completed")
        print(f"Result type: {type(result)}")
        print(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        print(f"Executed code: {result.get('executed_code', 'N/A')}")
        print(f"AI response: {result.get('ai_response', 'N/A')[:100]}...")
        
    except Exception as e:
        print(f"Error during function calling test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_function_calling())
