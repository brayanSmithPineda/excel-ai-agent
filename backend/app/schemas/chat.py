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

    #Temporary for testing without full auth system
    access_token: Optional[str] = Field(None, description="User's access token")
    refresh_token: Optional[str] = Field(None, description="User's refresh token")
class ChatResponse(BaseModel):
    """
    Response model for chat completion
    
    Fields:
        ai_response: The AI's response text
        conversation_id: ID for continuing this conversation
        search_results: Context found from searches (for transparency)
        tokens_used: Token count for billing/monitoring
    """
    ai_response: str = Field(description="AI's natural language response")
    conversation_id: str = Field(description="Conversation ID for continuity")
    
    # NEW: Code execution fields
    executed_code: bool = Field(default=False, description="Whether code was executed")
    code_output: Optional[str] = Field(None, description="Output from code execution")
    output_files: Optional[Dict[str, str]] = Field(None, description="Generated files (base64)")
    execution_reason: Optional[str] = Field(None, description="Why code was executed")
    
    # NEW: MEDIUM_RISK permission handling
    requires_permission: Optional[bool] = Field(None, description="Code needs user approval")
    risk_level: Optional[str] = Field(None, description="Risk level: low/medium/high")
    code_preview: Optional[str] = Field(None, description="Code to review before approval")
    
    # Search context (existing)
    search_results: Optional[Dict[str, Any]] = Field(None, description="Search results used")
    tokens_used: Optional[int] = Field(None, description="Estimated tokens")