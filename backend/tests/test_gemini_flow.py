"""
Test script for Gemini service.
"""
import asyncio
import sys
import os

#add the project root to the path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) #get the directory of the current file and go up one level to get the root of the project
sys.path.append(backend_dir) #add the project root to the path

from app.services.gemini_service import gemini_service
from app.config.database import get_supabase_client, supabase_manager

async def test_gemini_flow():
    try:
        test_user_id = "4532aa5d-bd5c-400d-bbc9-806c41111079"

        print("Test 1: New conversation and first message")
        #test 1: New conversation and first message
        response1 = await gemini_service.chat_completion(
            message = "Hello, can you help me create a simple SUM formula in Excel?",
            conversation_id = None,
            user_id = test_user_id
        )
        print(f"Response 1: {response1}")

        #Get the conversation ID from the database: This is to check  were creeated in supabase
        supabase = get_supabase_client()
        conversations = supabase.table('ai_conversations').select('id').eq('user_id', test_user_id).execute()

        if not conversations.data:
            raise Exception("No conversation found for user")
        
        conversation_id = conversations.data[0]['id']
        print(f"Created Conversation ID: {conversation_id}")

        print("Test 2: Existing conversation and message")
        #test 2: Existing conversation and message
        response2 = await gemini_service.chat_completion(
            message = "Can you show me a specifc example with cell references?",
            conversation_id = conversation_id, #continue existing conversation
            user_id = test_user_id
        )
        print(f"Response 2: {response2}")

        #check the messages in the conversation in supabase
        conversation_date = supabase.table('ai_conversations').select('messages, title').eq('id', conversation_id).single().execute()

        messages = conversation_date.data['messages']
        print(f"Conversation store successfully in supabase: Messages in the conversation: {messages}")
        print(f"Conversation title: {conversation_date.data['title']}")
        
        #test 3: Check audit logs in supabase
        audit_logs = supabase.table('audit_logs').select('action, status').eq('user_id', test_user_id).execute()
        print(f"Audit logs: {audit_logs.data}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Test completed")

if __name__ == "__main__":
    asyncio.run(test_gemini_flow())
