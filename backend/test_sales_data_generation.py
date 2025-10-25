#!/usr/bin/env python3
"""
Test script to verify the unified chat-executor interface
by asking it to generate a simple test file with 10 rows of sales data.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.gemini_service import GeminiService

async def test_sales_data_generation():
    """Test generating sales data with the unified interface"""
    print("Testing unified chat-executor interface...")
    print("Request: Generate a simple test file with 10 rows of sales data")
    print("=" * 60)
    
    try:
        # Initialize service
        service = GeminiService()
        print("GeminiService initialized")
        
        # Test with sales data generation request
        print("Testing with: 'Generate a simple test file with 10 rows of sales data'")
        result = await service.chat_completion(
            message='Generate a simple test file with 10 rows of sales data', 
            conversation_id=None, 
            user_id='3fdc19ef-75eb-460b-a9b1-ebc5b5b8436b'
        )
        
        print("Function calling test completed")
        print(f"Result type: {type(result)}")
        print(f"Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        print(f"Executed code: {result.get('executed_code', 'N/A')}")
        print(f"Execution reason: {result.get('execution_reason', 'N/A')}")
        print(f"AI response: {result.get('ai_response', 'N/A')}")
        
        if result.get('code_output'):
            print(f"Code output: {result.get('code_output', 'N/A')}")
        
        if result.get('output_files'):
            print(f"Generated files: {list(result.get('output_files', {}).keys())}")
        
        print("=" * 60)
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_sales_data_generation())
