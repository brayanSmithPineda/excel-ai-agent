#!/usr/bin/env python3
"""
Debug script to see what the service actually returns
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.gemini_service import GeminiService

async def test_service_response():
    """Test what the service actually returns"""
    print("=== DEBUGGING: Service Response Structure ===")
    print("=" * 60)
    
    try:
        # Initialize service
        service = GeminiService()
        print("GeminiService initialized")
        
        # Test message that should trigger function calling
        test_message = "Execute Python code to calculate 2+2"
        print(f"Test message: '{test_message}'")
        
        # Call service
        result = await service.chat_completion(
            message=test_message, 
            conversation_id=None, 
            user_id='3fdc19ef-75eb-460b-a9b1-ebc5b5b8436b'
        )
        
        print(f"\nService returned result:")
        print(f"   - Type: {type(result)}")
        print(f"   - Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        # Check each key
        for key in ['ai_response', 'conversation_id', 'executed_code', 'code_output', 'execution_reason']:
            value = result.get(key, 'KEY_NOT_FOUND')
            print(f"   - {key}: {value} (type: {type(value)})")
        
        # Check search-related keys
        for key in ['semantic_context', 'excel_functions', 'symbols']:
            value = result.get(key, 'KEY_NOT_FOUND')
            print(f"   - {key}: {value} (type: {type(value)})")
        
        print("\n" + "=" * 60)
        print("DEBUGGING COMPLETE")
        
    except Exception as e:
        print(f"Error during debugging: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_service_response())
