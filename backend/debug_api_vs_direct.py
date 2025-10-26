#!/usr/bin/env python3
"""
Debug script to compare direct service call vs API endpoint flow
"""
import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.services.gemini_service import GeminiService

async def test_direct_vs_api():
    """Compare direct service call vs API endpoint flow"""
    print("=== DEBUGGING: Direct Service Call vs API Endpoint ===")
    print("=" * 60)
    
    try:
        # Initialize service
        service = GeminiService()
        print("GeminiService initialized")
        
        # Test message that should trigger function calling
        test_message = "Execute Python code to calculate 2+2"
        print(f"Test message: '{test_message}'")
        
        print("\nSTEP 1: Testing direct service call...")
        print("-" * 40)
        
        # Direct service call
        result = await service.chat_completion(
            message=test_message, 
            conversation_id=None, 
            user_id='3fdc19ef-75eb-460b-a9b1-ebc5b5b8436b'
        )
        
        print(f"Direct call result:")
        print(f"   - Executed code: {result.get('executed_code', 'N/A')}")
        print(f"   - AI response: {result.get('ai_response', 'N/A')[:100]}...")
        print(f"   - Code output: {result.get('code_output', 'N/A')}")
        print(f"   - Execution reason: {result.get('execution_reason', 'N/A')}")
        
        print("\nSTEP 2: Testing API endpoint...")
        print("-" * 40)
        
        # Test API endpoint
        import requests
        api_url = "https://127.0.0.1:8000/api/v1/chat/completion"
        
        try:
            response = requests.post(
                api_url,
                json={
                    "message": test_message,
                    "conversation_id": None
                },
                verify=False,  # Skip SSL verification for localhost
                timeout=30
            )
            
            if response.status_code == 200:
                api_result = response.json()
                print(f"API call result:")
                print(f"   - Executed code: {api_result.get('executed_code', 'N/A')}")
                print(f"   - AI response: {api_result.get('ai_response', 'N/A')[:100]}...")
                print(f"   - Code output: {api_result.get('code_output', 'N/A')}")
                print(f"   - Execution reason: {api_result.get('execution_reason', 'N/A')}")
                
                # Compare results
                print("\nSTEP 3: Comparing results...")
                print("-" * 40)
                
                direct_executed = result.get('executed_code', False)
                api_executed = api_result.get('executed_code', False)
                
                if direct_executed == api_executed:
                    print("Both calls have same execution status")
                else:
                    print("DIFFERENCE FOUND!")
                    print(f"   - Direct call executed: {direct_executed}")
                    print(f"   - API call executed: {api_executed}")
                    
                    if direct_executed and not api_executed:
                        print("   - Direct call works, API call doesn't execute code")
                        print("   - This suggests API endpoint has different behavior")
                
            else:
                print(f"API call failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"API call error: {str(e)}")
        
        print("\n" + "=" * 60)
        print("DEBUGGING COMPLETE")
        
    except Exception as e:
        print(f"Error during debugging: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_direct_vs_api())
