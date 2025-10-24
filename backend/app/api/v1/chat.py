"""
Chat Completion API Endpoint

Exposes GeminiService.chat_completion() to frontend for intelligent conversational AI.
Includes semantic search, Excel function search, and hybrid search capabilities.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List, Dict, Any
from loguru import logger

from app.auth.dependencies import get_current_user
from app.services.gemini_service import GeminiService
from app.schemas.auth import UserProfile
from app.schemas.chat import ChatRequest, ChatResponse
# Create router
router = APIRouter(prefix="/chat", tags=["chat"])



# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/completion", response_model=ChatResponse)
async def chat_completion(
    request: ChatRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)  # ✅ Enable JWT validation
):
    """
    Main chat completion endpoint with intelligent search
    
    This endpoint:
    1. Takes user message
    2. Searches past conversations (semantic search) if enabled
    3. Searches Excel function database if enabled
    4. Searches workbook symbols (hybrid search) if enabled
    5. Generates context-aware AI response
    6. Returns response with conversation ID for continuity
    
    Args:
        request: ChatRequest with message and search preferences
        current_user: Authenticated user (from JWT token)
    
    Returns:
        ChatResponse with AI response and conversation ID
    """
    try:
        # Extract user_id from validated JWT token
        user_id = current_user.get("sub") or current_user.get("user_id")
        logger.info(f"Chat completion request from authenticated user {user_id}: {request.message[:50]}...")

        # Using admin client for database operations - no authentication needed
        # Initialize Gemini service for this user
        gemini_service = GeminiService()

        # Call the intelligent chat completion method
        result = await gemini_service.chat_completion(
            message=request.message,
            conversation_id=request.conversation_id,
            user_id=user_id
        )

        # Extract search results for transparency (optional)
        search_results = {
            "semantic_matches": len(result.get("semantic_context", [])) if request.enable_semantic_search and "semantic_context" in result else 0,
            "excel_functions": len(result.get("excel_functions", [])) if request.enable_excel_search and "excel_functions" in result else 0,
            "workbook_symbols": len(result.get("symbols", [])) if request.enable_hybrid_search and "symbols" in result else 0
        }

        return ChatResponse(
            ai_response=result["ai_response"],
            conversation_id=result["conversation_id"],
            search_results=search_results,
            tokens_used=result.get("tokens_used")
        )

    except Exception as e:
        logger.error(f"Chat completion failed for user {user_id}: %s",e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat completion failed: {str(e)}"
        )