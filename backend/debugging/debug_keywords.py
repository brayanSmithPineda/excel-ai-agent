import asyncio
import sys
import os

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

from app.services.gemini_service import gemini_service

async def debug_keywords():
    """Enhanced debugging for keyword search issues"""

    print("=== Enhanced Database Content Check ===")

    try:
        # Check specifically for VLOOKUP and lookup-related functions
        vlookup_check = gemini_service.supabase.table('excel_functions').select('function_name, keywords, description').eq('function_name', 'VLOOKUP').execute()

        print("VLOOKUP function details:")
        if vlookup_check.data:
            func = vlookup_check.data[0]
            print(f"Function: {func['function_name']}")
            print(f"Keywords: {func['keywords']}")
            print(f"Description: {func['description']}")
        else:
            print("VLOOKUP not found!")

        print("\n" + "="*50)

        # Search for functions that might contain 'lookup' in keywords
        print("\nSearching for 'lookup' in keywords manually:")
        all_functions = gemini_service.supabase.table('excel_functions').select('function_name, keywords').execute()

        lookup_matches = []
        for func in all_functions.data:
            if func.get('keywords'):
                for keyword in func['keywords']:
                    if 'lookup' in keyword.lower():
                        lookup_matches.append(func)
                        break

        print(f"Found {len(lookup_matches)} functions with 'lookup' in keywords:")
        for func in lookup_matches:
            print(f"- {func['function_name']}: {func['keywords']}")

        print("\n" + "="*50)

        # Search for functions that might contain 'combine' or 'text' in keywords/description
        print("\nSearching for 'combine' or 'text' related functions:")
        text_matches = []
        for func in all_functions.data:
            # Check keywords
            if func.get('keywords'):
                for keyword in func['keywords']:
                    if 'combine' in keyword.lower() or 'join' in keyword.lower() or 'merge' in keyword.lower():
                        text_matches.append(func)
                        break

        print(f"Found {len(text_matches)} functions with text-related keywords:")
        for func in text_matches:
            print(f"- {func['function_name']}: {func['keywords']}")

    except Exception as e:
        print(f"Error in enhanced debugging: {e}")

if __name__ == "__main__":
    asyncio.run(debug_keywords())