"""
Test script for vector search.
"""
import asyncio
import sys
import os
import requests
from loguru import logger


#add the project root to the path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) #get the directory of the current file(the partent is the tests directory) and go up one level to get the root of the project(the backend directory)
sys.path.append(backend_dir) #add the project root to the path
#what this does is it allows us to import using app 

from app.services.gemini_service import gemini_service
from app.config.database import get_supabase_client, supabase_manager

async def test_vector_search():
    """
    Test vector search.
    """
    try:
        #Get existing conversation from the database
        supabase = get_supabase_client()
        #Authenticate the user
        auth_response = supabase.auth.sign_in_with_password(
            {
                "email": "gemini_test_user@gmail.com",
                "password": "gemini_test_password"
            }
        )
        
        if auth_response.user and auth_response.session:
            print("User authenticated successfully")
        else:
            raise Exception("Failed to authenticate user")
        
        conversations = supabase.table('ai_conversations').select('id, messages, user_id').eq('user_id', auth_response.user.id).limit(3).execute()

        if not conversations.data:
            raise Exception("No conversation found for user, create some conversations first")
        
        print(f"Found {len(conversations.data)} conversations to test vector search")

        for conv in conversations.data:
            conversation_id = conv['id']
            user_id = conv['user_id']

            #Check if embeddings are already created for this conversation
            existing = supabase.table('conversation_embeddings').select('id').eq('conversation_id', conversation_id).execute()

            if existing.data:
                print(f"Skipping conversation {conversation_id} - embeddings already exist")
                continue
            
            #Create the chunks and embeddings for the conversation that not have embeddings yet
            chunks = await gemini_service._chunk_conversation(conversation_id)

            for chunk_data in chunks:
                embedding_id = await gemini_service._create_conversation_embedding(
                    conversation_id = chunk_data['conversation_id'], 
                    user_id = chunk_data['user_id'], 
                    chunk_text = chunk_data['chunk_text'], 
                    chunk_index = chunk_data['chunk_index'], 
                    metadata = chunk_data['metadata']
                )

                print(f"Created embedding {embedding_id} for chunk {chunk_data['chunk_text']}")

        # Test semantic similarity search
        test_query = "How do i use VLOOKUP in excel?"
        test_user_id = conversations.data[0]['user_id'] #test with the first user_id in the ai_conversations table

        results = await gemini_service.semantic_similarity_search(
            query = test_query,
            user_id = test_user_id,
            limit = 3,
            similarity_threshold = 0.5 #lower threshold for testing
        )
        
        #display the results
        print(f"{len(results)} results found for query '{test_query}'")
        for i, result in enumerate(results, 1): #is is going to hold the index of the result and result is going to hold the result itself, 1 means start from 1
            print(f"\n--- Result {i} ---")
            print(f"Conversation ID: {result['conversation_id']}")
            print(f"Similarity Score: {result['similarity_score']:.3f}")
            print(f"Distance: {result['distance']:.3f}")
            print(f"Chunk Text Preview: {result['chunk_text'][:200]}...")
            print(f"Metadata: {result['metadata']}")

        print(f"\n🎉 Vector search test completed successfully!")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        raise e


if __name__ == "__main__": #this is to run the test_vector_search function when the script is executed directly not when it is imported
    asyncio.run(test_vector_search()) #this asyncio.run is going to run the test_vector_search function asynchronously