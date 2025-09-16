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
        """
        try:
            if not user_id:
                raise Exception("User ID is required")
            
            if access_token and refresh_token:
                self.supabase.auth.set_session(access_token, refresh_token = refresh_token)
            
            if not conversation_id: #if no previous conversation, create a new one
                #First create a new conversation in supabase
                conversation_id = await self._create_new_chat(user_id, message)

                #Then create a new chat session (no history for a new chat)
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
                    history = None # no history for a new chat
                )
            else: #if there is a previous conversation, use it, this method is going to have the chat history
                chat = self._get_existing_chat(conversation_id)
            
            #send_message is a method of the chat object, it contains the message to send and some metadata about the response.
            response = chat.send_message(message)

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
#Create an instance of the GeminiService class
gemini_service = GeminiService()

