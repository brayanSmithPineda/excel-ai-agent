"""
This service is responsible for interacting with the Gemini API.
"""
from typing import TYPE_CHECKING, Optional, List
from google import genai
from google.genai import types
from app.config.settings import settings
from loguru import logger
from app.config.database import get_supabase_client, get_supabase_admin_client
from datetime import datetime
import re

if TYPE_CHECKING:
    from google.genai.chats import Chat

class GeminiService:

    def __init__(self):
        # Get API key from settings (which loads from .env file)
        if not settings.gemini_api_key:
            raise ValueError("GEMINI_API_KEY is required but not found in environment variables")

        client = genai.Client(api_key=settings.gemini_api_key.get_secret_value())
        self.client = client
        #Add Supabase for phase 1: Direct History (Pass last n messages to Gemini)
        self.supabase = get_supabase_client()
    
    async def chat_completion(self, message: str, conversation_id: Optional[str] = None, user_id: str = None, access_token: str = None, refresh_token: str = None) -> str:
        """
        Send a message to the Gemini API and return the response.
        Use , direct history, semantic search, and lexical search to answer the question.
        """
        try:
            if not user_id:
                raise Exception("User ID is required")
            
            if access_token and refresh_token:
                self.supabase.auth.set_session(access_token, refresh_token = refresh_token)
            
            #Add semantic search for context from similar past conversations
            relevant_context = ""
            try:
                #search for semantically similar past conversations
                similar_chunks = await self.semantic_similarity_search(
                    query = message,
                    user_id = user_id,
                    limit = 3,
                    similarity_threshold = 0.8
                )

                if similar_chunks:
                    context_parts = []
                    for chunk in similar_chunks:
                        context_parts.append(f"Previous conversation context: {chunk['chunk_text']}")
                    relevant_context = "\n\n".join(context_parts)
                else:
                    logger.info(f"No relevant past conversation found for this query")
                
            except Exception as e:
                logger.warning(f"Error performing semantic similarity search, continuing without context: {e}")
                pass
                
            enhanced_message = message
            if relevant_context:
                enhanced_message = f"""User's current question: {message}
                Relevant context from user's past Excel conversations:
                {relevant_context}

                Please answer the current question, and reference past context when helpful.
                """ #this is the message we past to the AI , it contains the user's current question and the relevant context from the past conversations
            
            if not conversation_id: #if no previous conversation, create a new one
                #First create a new conversation in supabase, use the original message for the title
                conversation_id = await self._create_new_chat(user_id, message)

                #Then create a new chat session (no history for a new chat)
                chat = self.client.chats.create(
                    model = "gemini-2.0-flash",
                    config = types.GenerateContentConfig(
                        system_instruction = "You are an excel expert that can answer questions and help with tasks. Use any provided context from the user's past conversations to give more personalized and relevant assistance.",
                        response_mime_type = "text/plain",
                        safety_settings= [
                            types.SafetySetting(
                                category='HARM_CATEGORY_HATE_SPEECH',
                                threshold='BLOCK_ONLY_HIGH'
                            ),
                        ]
                    ),
                    history = None # no history for a new chatf
                )
            else: #if there is a previous conversation, use it, this method is going to have the chat history
                chat = self._get_existing_chat(conversation_id)

            #send_message is a method of the chat object, it contains the message to send and some metadata about the response.
            response = chat.send_message(enhanced_message)

            #Save the messages (user message and ai response) to supabase
            await self._append_messages(conversation_id, message, response.text)

            #Add audit log to track the interaction in audit_logs table in supabase
            await self._log_ai_interaction(user_id, conversation_id, message, response.text)

            return response.text
            
        except Exception as e:
            logger.error(f"Error sending message to Gemini API: {e}")

            #if user_id and conversation_id are available, log the failed interaction
            if user_id and 'conversation_id' in locals() and conversation_id: #locals() is a built-in function that returns a dictionary of local variables
                try:
                    await self._log_failed_ai_interaction(user_id, conversation_id, message, str(e))
                except Exception as e:
                    pass

            raise e
    
    async def semantic_similarity_search(self, query: str, user_id: str, limit: int = 5, similarity_threshold: float = 0.8) -> List[dict]:
        """
        Takes a query and returns a list of chunks that are semantically similar to the query. Basically, Find past
        conversation that are semantically similar to the query.
        Args:
            query: the query to search for.
            user_id: the id of the user.
            limit: the number of chunks to return.
            similarity_threshold: the similarity threshold for the chunks, this is what we expect the similarity to be.
        Return: a list of chunks that are semantically similar to the query based on the similarity threshold.
        """
        try:
            # Generate embedding vector for the query
            query_embedding = await self.generate_embedding(query)

            # Call our supabase database function to find similar conversations
            similar_conversations = self.supabase.rpc('similarity_search_conversations', {
                'query_embedding': query_embedding,
                'target_user_id': user_id,
                'match_threshold': similarity_threshold,
                'match_count': limit
            }).execute()

            #Process and return the results
            results = []
            for similar_conversation in similar_conversations.data:
                #Convert database result to structured format
                result_item = {
                    'conversation_id': similar_conversation.get('conversation_id'),
                    'chunk_text': similar_conversation.get('chunk_text'),
                    'similarity_score': 1.0 - similar_conversation.get('distance', 1.0), #This converts distance like 0.2 to 0.8, so the higher the distance, the more similar the chunk is to the query.
                    'metadata': similar_conversation.get('metadata', {}),
                    'created_at': similar_conversation.get('created_at'),
                    'distance': similar_conversation.get('distance'),
                }
                results.append(result_item)
                
            logger.info(f"Found {len(results)} semantically similar chunks for user {user_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error performing semantic similarity search: {e}")
            raise e

    async def excel_function_search(self, query: str, limit: int = 10) -> List[dict]:
        """
        Multi-strategy search for Excel functions combining:
        - Exact function name matching (Highest priority)
        - Fuzzy name matching with similarity scoring
        - Keyword array search
        - Full-text description search
        - Category filtering
        Return: a list of Excel functions that match the query.
        """
        try:
            #Clean the query
            clean_query = query.strip().upper()
            result = []

            #Strategy 1: Exact function name matching (Highest priority)
            exact_match = self.supabase.table('excel_functions').select('*').eq('function_name', clean_query).execute()

            if exact_match.data:
                for function in exact_match.data:
                    function['relevance_score'] = 100 #Set the highest priority score for exact matches
                    function['match_type'] = 'exact'
                    result.append(function)
            
            #Strategy 2: Fuzzy name matching with similarity scoring (Starts with query)
            if len(result) < limit:
                prefix_match = self.supabase.table('excel_functions').select('*').like('function_name', f'{clean_query}%').execute()
                for function in prefix_match.data:
                    #avoid duplicates from exact match
                    if not any(r['id'] == function['id'] for r in result):
                        function['relevance_score'] = 80 #Set the second medium priority score for prefix matches
                        function['match_type'] = 'prefix'
                        result.append(function)
            
            #Strategy 3: Keyword array search
            if len(result) < limit:
                try:
                    #Try first exact list match look for 'lookup' in the list ['vertical lookup', 'search', 'find', 'table lookup']
                    keyword_match = self.supabase.table('excel_functions').select('*').overlaps('keywords', [query.lower()]).execute()
                    for function in keyword_match.data:
                        if not any(r['id'] == function['id'] for r in result):
                            function['relevance_score'] = 60 #Set the third low priority score for keyword matches
                            function['match_type'] = 'keyword'
                            result.append(function)
                    #if not exact match, try to find partial match in the list
                    if len([r for r in result if r.get('match_type') == 'keyword']) == 0:
                        all_functions = self.supabase.table('excel_functions').select('*').execute()
                        for function in all_functions.data:
                            if function.get('keywords') and not any(r['id'] == function['id'] for r in result):
                                # Check if query partially matches any keyword
                                for keyword in function['keywords']:
                                    if query.lower() in keyword.lower():
                                        function['relevance_score'] = 60
                                        function['match_type'] = 'keyword_partial'
                                        result.append(function)
                                        break #break the loop if we found a match, to avoid adding the same function multiple times

                except Exception as e:
                    logger.error(f"Error performing keyword array search: {e}")
                    pass

            #Strategy 4: Full-text description search
            if len(result) < limit:
                #First try exact match
                desc_match = self.supabase.table('excel_functions').select('*').ilike('description', f'%{query}%').execute()
                for function in desc_match.data:
                    if not any(r['id'] == function['id'] for r in result):
                        function['relevance_score'] = 40 #Set the fourth low priority score for description matches
                        function['match_type'] = 'description'
                        result.append(function)
            
                #If not exact phrase math and query has multiple words, search for all words 
                if len([r for r in result if r.get('match_type') == 'description']) == 0 and ' ' in query:
                    words = [word.strip() for word in query.split() if len(word.strip()) > 2] #skip words less than 3 characters
                    if words:
                        all_functions = self.supabase.table('excel_functions').select('*').execute()
                        for function in all_functions.data:
                            if not any(r['id'] == function['id'] for r in result): # if not already in the result
                                description = function.get('description', '').lower()
                                #check if all words are in the description
                                if all(word in description for word in words):
                                    function['relevance_score'] = 35
                                    function['match_type'] = 'description_multi_word'
                                    result.append(function)

            #Sort by relevance score
            result.sort(key=lambda x: x['relevance_score'], reverse=True)
            limited_result = result[:limit]
            logger.info(f"Found {len(limited_result)} Excel functions for query: {query}")
            return limited_result
        
        except Exception as e:
            logger.error(f"Error performing excel function search: {e}")
            raise e

    async def _create_new_chat(self, user_id: str, first_message: str) -> str:
        """
        We need to first sabe the conversation to supabase before send the message to Gemini.
        This method  allows us to create a new conversation and save it to supabase, and return the conversation id.
        which will be used to send the message to Gemini.
        This is going to be used in the chat_completion method.
        """
        try:
            #generate a title for the conversation
            title = first_message[:50] + "..." if len(first_message) > 50 else first_message

            #create a new conversation in supabase
            conversation_data = {
                'user_id': user_id,
                'title': title,
                'messages': [], #empty array for now, messages will be added later after ai response with the _append_messages method
                'status': 'active'
            }

            #Insert the conversation into supabase
            result = self.supabase.table('ai_conversations').insert(conversation_data).execute()
            
            if not result.data:
                raise Exception("Failed to create new conversation in Supabase")
            
            conversation_id = result.data[0]['id']
            return conversation_id
        
        except Exception as e:
            logger.error(f"Error creating new chat in Supabase: {e}")
            raise e

    async def _append_messages(self, conversation_id: str, user_message: str, ai_response: str):
        """
        Append new user message and ai response to existing conversation in supabase.
        this mantain the conversion history in supabase.
        """
        try:
            # Get current conversation messages
            current = self.supabase.table('ai_conversations').select('messages').eq('id', conversation_id).single().execute()

            if not current.data:
                raise Exception("Conversation not found in Supabase")

            messages = current.data.get('messages', [])

            # create timestamp for both messages
            timestamp = datetime.utcnow().isoformat()

            # Append new user message and ai response
            messages.extend([
                {'role': 'user', 'content': user_message, 'timestamp': timestamp},
                {'role': 'model', 'content': ai_response, 'timestamp': timestamp}
            ])

            # Update conversation in supabase
            self.supabase.table('ai_conversations').update({
                'messages': messages,
                'updated_at': timestamp
            }).eq('id', conversation_id).execute()

        except Exception as e:
            logger.error(f"Error appending messages to conversation in Supabase: {e}")
    
    def _get_existing_chat(self, conversation_id: str) -> "Chat":
        """
        Retrieve existing conversation history and create a chat session with that history.
        This method fetches the messages from Supabase and formats them for Gemini
        """
        try:
            #Phase1: Query ai_conversations to get the messages
            conversation = self.supabase.table('ai_conversations').select('messages').eq('id', conversation_id).single().execute()

            messages = conversation.data.get('messages', [])

            #Phase1: Apply a sliding window to the messages (keep the last 20 messages for context)
            MAX_HISTORY_MESSAGE = 20      
            recent_message = messages[-MAX_HISTORY_MESSAGE:] if len(messages) > MAX_HISTORY_MESSAGE else messages

            #Phase1: Convert Supabase JSONB to Gemini Content format
            history = []
            for msg in recent_message:
                if msg['role'] == 'user':
                    #types.UserContent(parts=[msg['content']]) is a class that represents a user message, it contains the content of the message and the role of the message
                    #that class is from the google.genai import types
                    content = types.UserContent(parts=[msg['content']])
                elif msg['role'] == 'model':
                    content = types.ModelContent(parts=[msg['content']])
                else:
                    continue #skip the message if it is not a user or model message
                history.append(content)
            
            #Phase1: Count tokens and truncate if needed
            if history:
                #count tokens for the history
                history_text = self._format_history_for_counting(history)
                token_response = self._estimate_tokens(history_text)
                
                logger.info(f"Conversation {conversation_id} history: {token_response.total_tokens} tokens")

                #Apply smart truncation to stay under the token limit
                MAX_HISTORY_TOKENS = 800000
                if token_response.total_tokens > MAX_HISTORY_TOKENS:
                    logger.warning(f"History too long ({token_response.total_tokens} tokens), applying smart truncation")
                    history = self._smart_truncate(history, MAX_HISTORY_TOKENS)

            #Phase1: Create a chat session with the history
            chat = self.client.chats.create(
                model = "gemini-2.0-flash",
                config = types.GenerateContentConfig(
                    system_instruction = "You are an excel expert that can answer questions and help with tasks.",
                    response_mime_type = "text/plain",
                    safety_settings= [
                        types.SafetySetting(
                            category='HARM_CATEGORY_HATE_SPEECH',
                            threshold='BLOCK_ONLY_HIGH'
                        ),
                    ]
                ),
                history = history
            )
            return chat

        except Exception as e:
            logger.error(f"Error fetching conversation history from Supabase: {e}")
            raise e
        
    async def analyze_excel_data(self, data: List[List], user_question: str):
        """
        Analye Excel data and provide insights or answers to the user's question.
        """
        
    def _estimate_tokens(self, text: str) -> types.CountTokensResponse:
        """
        Take a text and return the number of tokens it contains. This is used to estimate the cost of the request.
        """
        try:
            response = self.client.models.count_tokens(
                model = "gemini-2.0-flash",
                contents = text
            )
            return response
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            raise e
        return response

    def _format_history_for_counting(self, history: List) -> str:
        """
        Convert Gimini history format to text for token counting.
        This helps estimate total token before sending the request to Gemini.
        Input: history is a list of content objects. for example looks like this:
        [
            types.UserContent(parts=['Hello, how are you?']),
            types.ModelContent(parts=['I am good, thank you!'])
        ]
        Output: a string of the history in text format. for example looks like this:
        "Hello, how are you? I am good, thank you!"
        """
        try:
            text_parts = []
            for content in history:
                #hasattr is a built-in function that checks if an object has an attribute
                if hasattr(content, 'parts') and content.parts:
                    #extract text from UserContent or ModelContent
                    for part in content.parts:
                        if hasattr(part, "text"):
                            text_parts.append(part.text)
                        elif isinstance(part, str):
                            text_parts.append(part)
                        else:
                            text_parts.append(str(part))
            #join the text parts with a space
            return ' '.join(text_parts)
        
        except Exception as e:
            logger.error(f"Error formatting history for token counting: {e}")
            raise e

    def _smart_truncate(self, history: List, max_tokens: int = 800000) -> List:
        """
        Truncate history to stay under the token limit.
        """
        try:
            if not history:
                return []
            
            truncated_history = []
            current_tokens = 0

            #Reverse the history to prioritize recent messages
            for content in reversed(history):
                if hasattr(content, 'parts') and content.parts:
                    message_text = " ".join(str(part) for part in content.parts if isinstance(part, str))
                    #Estimate tokens for the message
                    message_tokens = self._estimate_tokens(message_text).total_tokens

                    #Check if adding this message would exceed the limit
                    if current_tokens + message_tokens > max_tokens:
                        logger.info(f"Truncating history to stay under the token limit. Current tokens: {current_tokens}, Message tokens: {message_tokens}, Max tokens: {max_tokens}")
                        break

                    truncated_history.insert(0, content)
                    current_tokens += message_tokens
                
                #Always keep at least 2 messages in the history even if it exceeds the token limit
                if len(truncated_history) < 2 and len(history) >= 2:
                    logger.warning(f"History is too long, but we need to keep at least 2 messages. Current tokens: {current_tokens}, Max tokens: {max_tokens}")
                    return history[-2:]
            
            return truncated_history
        
        except Exception as e:
            logger.error(f"Error truncating history: {e}")
            raise e

    async def _log_ai_interaction(self, user_id: str, conversation_id: str, user_message: str, ai_response: str):
        """
        Log AI interaction to audit_logs table for compliance and monitoring.
        This tracks every AI query for security and usage monitoring.
        """
        try:
            # Prepare audit log data
            audit_data = {
                'user_id': user_id,
                'action': 'ai_query',
                'resource_type': 'conversation',
                'resource_id': conversation_id,
                'details': {
                    'user_message': user_message,
                    'ai_response': ai_response,
                    'model': 'gemini-2.0-flash',
                    'token_usage': {
                        'input_tokens': self._estimate_tokens(user_message).total_tokens,
                        'output_tokens': self._estimate_tokens(ai_response).total_tokens,
                        'total_tokens': self._estimate_tokens(user_message + ai_response).total_tokens
                    },
                    'timestamp': datetime.utcnow().isoformat()
                },
                'status': 'success'
            }

            # Insert audit log into Supabase
            result = self.supabase.table('audit_logs').insert(audit_data).execute()

            if result.data:
                logger.info(f"Audit logged AI interaction for user {user_id} in conversation {conversation_id}")
            else:
                logger.warning(f"Failed to log AI interaction audit for user {user_id}")

        except Exception as e:
            logger.error(f"Error logging AI interaction audit: {e}")

    async def _log_failed_ai_interaction(self, user_id: str, conversation_id: str, user_message: str, error_message: str):
        """
        Log failed AI interaction attempts for debugging and monitoring.
        """
        try:
            audit_data = {
                'user_id': user_id,
                'action': 'ai_query_failed',
                'resource_type': 'conversation',
                'resource_id': conversation_id,
                'details': {
                    'user_message': user_message,
                    'error': error_message,
                    'model': 'gemini-2.0-flash',
                    'timestamp': datetime.utcnow().isoformat()
                },
                'status': 'failure'
            }

            self.supabase.table('audit_logs').insert(audit_data).execute()
            logger.info(f"Audit logged failed AI interaction for user {user_id}")

        except Exception as e:
            logger.error(f"Error logging failed AI interaction: {e}")

    async def generate_embedding(self, text: str, task_type: str = "SEMANTIC_SIMILARITY") -> List[float]:
        f"""
        Generate embedding from text using gemini-embedding-001 model.
        Basically turns a text into a vector of numbers. like this [0.1, 0.2, 0.3, ...] (# dimensions 768)
        
        Args:
            text: the text to generate embedding from.
            task_type: the type of task to generate embedding for.
                - "SEMANCTIC_SIMILARITY": check how similar in meaning strings of texts are. Check google docs for more details about the task_type.
        Return: a list of float values representing the embedding.
        """
        try:
            #use gemini-embedding-001 model to generate embedding
            response = self.client.models.embed_content(
                model = "gemini-embedding-001",
                contents = text,
                config = types.EmbedContentConfig(
                    task_type = task_type,
                    output_dimensionality = 768
                )
            )

            #Extract the embedding vector from the response
            embedding_vector = response.embeddings[0].values
            return embedding_vector

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise e

    async def _create_conversation_embedding(self, conversation_id: str, user_id: str, chunk_text: str, chunk_index: int,
        metadata: dict = None) -> str:
        """
        Create and store an embedding vector for a chunk of conversation and store it in the conversation_embeddings table in supabase.
        Args:
            conversation_id: the id of the conversation.
            user_id: the id of the user.
            chunk_text: the text of the chunk.
            chunk_index: the index of the chunk.
            metadata: the metadata of the chunk.
        Return: the id of the created embedding in supabase.
        """
        try:
            #Generate embedding for the chunk
            embedding_vector = await self.generate_embedding(chunk_text)

            #Prepare metadata with default values
            chunk_metadata = metadata or {} 
            chunk_metadata.update({
                'chunk_length': len(chunk_text),
                'created_at': datetime.utcnow().isoformat()
            })

            #Insert embedding into supabase
            embedding_data = {
                'conversation_id': conversation_id,
                'user_id': user_id,
                'chunk_text': chunk_text,
                'embedding': embedding_vector,
                'chunk_index': chunk_index,
                'metadata': chunk_metadata,
            }

            result = self.supabase.table('conversation_embeddings').insert(embedding_data).execute()

            if not result.data:
                raise Exception("Failed to create conversation embedding in Supabase")

            embedding_id = result.data[0]['id']
            return embedding_id
        
        except Exception as e:
            logger.error(f"Error creating conversation embedding in Supabase: {e}")
            raise e

    async def _chunk_conversation(self, conversation_id: str) -> List[str]:
        """
        Intelligently chunk a conversation into semantically meaningful chunks/segments.
        Args:
            conversation_id: the id of the conversation.
        Return: a list of chunks/segments with text, metadata, and context.
        """
        try:
            # Get the full conversation from Supabase
            conversation = self.supabase.table('ai_conversations').select('messages, user_id').eq('id',conversation_id).single().execute()

            if not conversation.data:
                raise Exception(f"Conversation {conversation_id} not found")

            messages = conversation.data.get('messages', [])
            user_id = conversation.data.get('user_id')

            if len(messages) < 2:  # Need at least user + AI message
                return []

            chunks = []
            current_chunk_messages = []
            chunk_index = 0

            # Process messages in pairs (user + AI response)
            for i in range(0, len(messages) - 1, 2):
                if i + 1 < len(messages):
                    user_msg = messages[i]
                    ai_msg = messages[i + 1]

                    # Validate message roles
                    if user_msg.get('role') == 'user' and ai_msg.get('role') == 'model':
                        current_chunk_messages.extend([user_msg, ai_msg])

                        # Decision point: Should we create a chunk here?
                        if self._should_create_chunk(current_chunk_messages, i):
                            chunk_data = self._create_chunk_data(
                                messages=current_chunk_messages,
                                conversation_id=conversation_id,
                                user_id=user_id,
                                chunk_index=chunk_index
                            )
                            chunks.append(chunk_data)

                            # Reset for next chunk
                            current_chunk_messages = []
                            chunk_index += 1

            # Handle remaining messages in final chunk
            if current_chunk_messages:
                chunk_data = self._create_chunk_data(
                    messages=current_chunk_messages,
                    conversation_id=conversation_id,
                    user_id=user_id,
                    chunk_index=chunk_index
                )
                chunks.append(chunk_data)

            logger.info(f"Created {len(chunks)} intelligent chunks for conversation {conversation_id}")
            return chunks

        except Exception as e:
            logger.error(f"Error chunking conversation {conversation_id}: {e}")
            raise e 
    
    def _should_create_chunk(self, current_message: List[str], message_index: int) -> bool:
        """
        Intelligent decision making for when to create a new chunk.
        Factors: length, topic changes, excel function mentions, etc.
        """
        MAX_MESSAGE_PER_CHUNK = 8 # basically 4 user-ai exchanges
        if len(current_message) >= MAX_MESSAGE_PER_CHUNK:
            return True
        
        #Create a chunk if the total text length exceeds limit
        total_text = ' '.join(msg.get('content', '') for msg in current_message)
        MAX_CHUNK_CHARS = 1500
        if len(total_text) > MAX_CHUNK_CHARS:
            return True

        #Topic change dectection (look for Excel function transition)
        if len(current_message) >= 4: #at least 2 exchanges
            recent_text = ' '.join(msg.get('content', '') for msg in current_message[-2:])
            earlier_text = ' '.join(msg.get('content', '') for msg in current_message[:-2])

            #Topic change detection: Different excel functions are used
            recent_functions = self._extract_excel_functions(recent_text)
            earlier_functions = self._extract_excel_functions(earlier_text)

            if recent_functions and earlier_functions and not recent_functions.intersection(earlier_functions):
                return True #Topic changed, create a new chunk

        return False

    def _create_chunk_data(self, messages: List[dict], conversation_id: str, user_id: str, chunk_index: int) -> dict:
        """
        Create a structured chunk with text and metadata
        """
        chunk_parts = []
        for msg in messages:
            role_label = "User" if msg.get('role') == 'user' else "Assistant"
            content = msg.get('content', '')
            chunk_parts.append(f"{role_label}: {content}")
        
        chunk_text = '\n\n'.join(chunk_parts)
        
        #Extract metadata for better search context
        all_text = ' '.join(msg.get('content', '') for msg in messages)
        excel_functions = self._extract_excel_functions(all_text)
        metadata = {
            'excel_functions_mentioned': list(excel_functions),
            'message_count': len(messages),
            'chunk_length': len(chunk_text),
            'has_formulas': self._contains_excel_formulas(all_text),
            'complexity_level': self._assess_complexity(all_text),
        }   
        return {
            'conversation_id': conversation_id,
            'user_id': user_id,
            'chunk_text': chunk_text,
            'chunk_index': chunk_index,
            'metadata': metadata,
        }
    
    def _extract_excel_functions(self, text: str) -> set:
        """
        Extract Excel functions mentioned in the text
        """
        # Common Excel functions pattern
        excel_functions = re.findall(r"\b(VLOOKUP|HLOOKUP|INDEX|MATCH|SUMIF|COUNTIF|PIVOT|XLOOKUP|SUMIFS|COUNTIFS|IF|AND|OR|NOT|CONCATENATE|LEFT|RIGHT|MID|LEN|TRIM|UPPER|LOWER|IFERROR|IFNA|IFS|SWITCH|CHOOSE)\b", text.upper())
        return set(excel_functions)
    
    def _contains_excel_formulas(self, text: str) -> bool:
        """
        Check if the text contains Excel formulas
        """
        return bool(re.search(r'=\w+\(', text))
    
    def _assess_complexity(self, text: str) -> str:
        """
        Assess complexity level of excel discussion
        """
        excel_functions = self._extract_excel_functions(text)
        if len(excel_functions) >= 3:
            return "complex"
        elif len(excel_functions) >= 1:
            return "intermediate"
        else:
            return "basic"
    
    
#Create an instance of the GeminiService class
gemini_service = GeminiService()

