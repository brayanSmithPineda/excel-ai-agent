import asyncio
from app.services.gemini_service import gemini_service
import sys
import os
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(backend_dir)

async def test_multiword_description():
    print("Testing multi-word description search...")

    # Test the problematic query
    result = await gemini_service.excel_function_search("combine text", limit=5)

    print(f"Results for 'combine text': {len(result)} found")
    for func in result:
        print(f"- {func['function_name']}: {func['match_type']} (score: {func['relevance_score']})")
        print(f"  Description: {func['description'][:100]}...")

if __name__ == "__main__":
    asyncio.run(test_multiword_description())