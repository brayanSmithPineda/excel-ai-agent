#!/usr/bin/env python3
"""
Simple test to check if Gemini function calling works at all
"""

import asyncio
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

async def test_simple_gemini():
    """Test basic Gemini function calling"""
    
    # Initialize Gemini
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    client = genai.Client()
    
    # Simple function declaration
    simple_tool = types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="calculate",
                description="Calculate a simple math expression",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "expression": types.Schema(
                            type=types.Type.STRING,
                            description="Math expression to calculate"
                        )
                    },
                    required=["expression"]
                )
            )
        ]
    )
    
    try:
        print("Testing simple Gemini function calling...")
        
        # Test with a simple request
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[{"role": "user", "parts": [{"text": "Calculate 2+2"}]}],
            tools=[simple_tool]
        )
        
        print(f"Response: {response}")
        print(f"Candidates: {response.candidates}")
        
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            print(f"Candidate content: {candidate.content}")
            print(f"Finish reason: {candidate.finish_reason}")
            
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    print(f"Part: {part}")
                    if hasattr(part, 'function_call') and part.function_call:
                        print(f"Function call: {part.function_call}")
                    if hasattr(part, 'text') and part.text:
                        print(f"Text: {part.text}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_gemini())
