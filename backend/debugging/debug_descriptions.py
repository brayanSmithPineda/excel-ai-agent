import asyncio
from app.services.gemini_service import gemini_service
import sys
import os
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)


async def debug_descriptions():
    """Debug description search"""

    print("=== Testing Description Search ===")

    # Check CONCATENATE description
    concat_check = gemini_service.supabase.table('excel_functions').select('function_name, description').eq('function_name','CONCATENATE').execute()

    if concat_check.data:
        func = concat_check.data[0]
        print(f"CONCATENATE description: {func['description']}")
        print()

    # Test different search terms
    test_terms = ["combine", "text", "combine text", "join", "merge"]

    for term in test_terms:
        print(f"\nTesting description search for: '{term}'")
        desc_match = gemini_service.supabase.table('excel_functions').select('function_name, description').ilike('description', f'%{term}%').execute()
        print(f"Found {len(desc_match.data)} results:")
        for func in desc_match.data:
            print(f"- {func['function_name']}")

if __name__ == "__main__":
    asyncio.run(debug_descriptions())