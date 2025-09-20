import asyncio
from app.services.gemini_service import gemini_service
import sys
import os
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

async def test_supabase_array_methods():
    """Test different Supabase methods for querying JSONB arrays"""

    print("=== Testing Supabase Array Query Methods ===")

    # First, let's see exactly what VLOOKUP has
    vlookup = gemini_service.supabase.table('excel_functions').select('function_name, keywords').eq('function_name','VLOOKUP').execute()

    if vlookup.data:
        keywords = vlookup.data[0]['keywords']
        print(f"VLOOKUP keywords: {keywords}")
        print(f"First keyword: '{keywords[0]}'")
        print()

    test_cases = [
        # Test with exact keyword match
        ("exact match", "vertical lookup"),
        # Test with partial keyword  
        ("partial match", "lookup"),
        # Test with array element
        ("array element", ["vertical lookup"]),
        # Test with multiple elements
        ("multiple elements", ["vertical lookup", "search"]),
    ]

    for test_name, test_value in test_cases:
        print(f"\n--- Testing {test_name}: {test_value} ---")

        # Method 1: contains
        try:
            result1 = gemini_service.supabase.table('excel_functions').select('function_name').contains('keywords',test_value).execute()
            print(f"contains(): Found {len(result1.data)} results")
            if result1.data:
                print(f"  Results: {[r['function_name'] for r in result1.data]}")
        except Exception as e:
            print(f"contains() failed: {e}")

        # Method 2: overlaps (only for arrays)
        if isinstance(test_value, list):
            try:
                result2 = gemini_service.supabase.table('excel_functions').select('function_name').contains('keywords',test_value).execute()
                print(f"overlaps(): Found {len(result2.data)} results")
                if result2.data:
                    print(f"  Results: {[r['function_name'] for r in result2.data]}")
            except Exception as e:
                print(f"overlaps() failed: {e}")

        # Method 3: cs (case sensitive contains)
        if isinstance(test_value, list):
            try:
                # Convert array to PostgreSQL array format
                pg_array = '{' + ','.join([f'"{item}"' for item in test_value]) + '}'
                result3 = gemini_service.supabase.table('excel_functions').select('function_name').cs('keywords',pg_array).execute()
                print(f"cs(): Found {len(result3.data)} results")
                if result3.data:
                    print(f"  Results: {[r['function_name'] for r in result3.data]}")
            except Exception as e:
                print(f"cs() failed: {e}")

    print("\n" + "="*60)
    print("TESTING POSTGRESQL OPERATORS DIRECTLY")

    # Test PostgreSQL array operators directly using rpc or raw SQL
    try:
        # Test @> operator (contains)
        result = gemini_service.supabase.rpc('test_array_contains', {
            'search_keywords': ['vertical lookup']
        }).execute()
        print(f"RPC test (if available): {result}")
    except Exception as e:
        print(f"RPC test not available: {e}")

if __name__ == "__main__":
    asyncio.run(test_supabase_array_methods())