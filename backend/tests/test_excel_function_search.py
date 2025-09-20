import asyncio
import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from app.services.gemini_service import gemini_service
from app.config.database import get_supabase_client

async def test_excel_function_search():
    """Test the excel function search"""
    try:
        #Authenticate
        supabase = get_supabase_client()
        auth_response = supabase.auth.sign_in_with_password({
            "email": "gemini_test_user@gmail.com",
            "password": "gemini_test_password"
        })
        
        user_id = auth_response.user.id
        print(f"✅ Authenticated as user: {user_id}")
        
        #Test 1: Exact function name matching
        print("test 1: Exact function name matching")
        results = await gemini_service.excel_function_search('VLOOKUP')

        for result in results:
            print(f"Function: {result['function_name']}, score: {result['relevance_score']}, type: {result['match_type']}")
        
        #Test 2: Fuzzy name matching with similarity scoring
        print("test 2: Fuzzy name matching with similarity scoring")
        results = await gemini_service.excel_function_search('lookup')

        for result in results:
            print(f"Function: {result['function_name']}, score: {result['relevance_score']}, type: {result['match_type']}")

        #Test 3: Description search
        print("test 3: Description search")
        results = await gemini_service.excel_function_search('combine text')

        for result in results:
            print(f"Function: {result['function_name']}, score: {result['relevance_score']}, type: {result['match_type']}")
    except Exception as e:
        print(f"Error: {e}")
        raise e

if __name__ == "__main__":
    asyncio.run(test_excel_function_search())
            
        