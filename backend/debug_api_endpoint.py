#!/usr/bin/env python3
"""
Debug script to test the API endpoint directly
"""
import requests
import json

def test_api_endpoint():
    """Test the API endpoint directly"""
    print("=== DEBUGGING: API Endpoint Direct Test ===")
    print("=" * 60)
    
    api_url = "https://127.0.0.1:8000/api/v1/chat/completion"
    
    # Test data
    test_data = {
        "message": "Execute Python code to calculate 2+2",
        "conversation_id": None
    }
    
    print(f"Testing API endpoint: {api_url}")
    print(f"Test data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(
            api_url,
            json=test_data,
            verify=False,  # Skip SSL verification for localhost
            timeout=30
        )
        
        print(f"\nResponse status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success! Response:")
            print(f"   - Executed code: {result.get('executed_code', 'N/A')}")
            print(f"   - AI response: {result.get('ai_response', 'N/A')[:100]}...")
            print(f"   - Code output: {result.get('code_output', 'N/A')}")
            print(f"   - Execution reason: {result.get('execution_reason', 'N/A')}")
        else:
            print(f"Error! Status: {response.status_code}")
            print(f"Response text: {response.text}")
            
            # Try to parse as JSON
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print("Could not parse error response as JSON")
        
    except Exception as e:
        print(f"Request failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_endpoint()
