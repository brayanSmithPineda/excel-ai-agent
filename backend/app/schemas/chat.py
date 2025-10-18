"""
Pydantic schemas for Chat API endpoints.

These schemas define the request/response structure for chat completion.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

# ============================================================================
# PYDANTIC SCHEMAS - Request and Response Models
# ============================================================================

class ChatRequest(BaseModel):
    """
    Request model for chat completion
    
    Fields:
        message: User's message/question
        conversation_id: Optional - Use existing conversation or create new one
        enable_semantic_search: Whether to search past conversations
        enable_excel_search: Whether to search Excel function database
        enable_hybrid_search: Whether to use full hybrid search (workbook symbols)
    """
    message: str = Field(..., min_length=1, description="User's message")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID")
    enable_semantic_search: bool = Field(True, description="Search past conversations")
    enable_excel_search: bool = Field(True, description="Search Excel functions")
    enable_hybrid_search: bool = Field(True, description="Full hybrid search")

class ChatResponse(BaseModel):
    """
    Response model for chat completion
    
    Fields:
        ai_response: The AI's response text
        conversation_id: ID for continuing this conversation
        search_results: Context found from searches (for transparency)
        tokens_used: Token count for billing/monitoring
    """
    ai_response: str
    conversation_id: str
    search_results: Optional[Dict] = Field(None, description="Search context used")
    tokens_used: Optional[int] = Field(None, description="Estimated tokens")