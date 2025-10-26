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
    request: ChatRequest
    # TEMPORARY: Disable JWT validation for testing
    # current_user: Dict[str, Any] = Depends(get_current_user)
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
        # TEMPORARY: Use hardcoded test user ID for testing
        user_id = "3fdc19ef-75eb-460b-a9b1-ebc5b5b8436b"  # Test user ID
        logger.info(f"Chat completion request from test user {user_id}: {request.message[:50]}...")

        # Using admin client for database operations - no authentication needed
        # Initialize Gemini service for this user
        gemini_service = GeminiService()

        # Call the intelligent chat completion method
        result = await gemini_service.chat_completion(
            message=request.message,
            conversation_id=request.conversation_id,
            user_id=user_id,
            workbook_data=request.workbook_data
        )
        
        # Debug logging
        logger.info(f"Service returned result type: {type(result)}")
        if isinstance(result, dict):
            logger.info(f"Service returned keys: {list(result.keys())}")
        else:
            logger.error(f"Service returned non-dict result: {result}")

        # Extract search results for transparency (optional)
        # Use the search_results from the service response if available
        search_results = result.get("search_results", {
            "semantic_matches": 0,
            "excel_functions": 0,
            "workbook_context": False
        })

        return ChatResponse(
            ai_response=result["ai_response"],
            conversation_id=result["conversation_id"],
            search_results=search_results,
            tokens_used=result.get("tokens_used"),
            # Code execution fields
            executed_code=result.get("executed_code", False),
            code_output=result.get("code_output"),
            output_files=result.get("output_files"),
            execution_reason=result.get("execution_reason"),
            # NEW: Formula writing fields
            write_formulas=result.get("write_formulas", False),
            office_js_code=result.get("office_js_code"),
            formula_reason=result.get("formula_reason"),
            target_column=result.get("target_column"),
            formula_description=result.get("formula_description"),
            # Permission request fields
            requires_permission=result.get("requires_permission"),
            risk_level=result.get("risk_level"),
            code_preview=result.get("code_preview")
        )

    except Exception as e:
        logger.error(f"Chat completion failed for user {user_id}: %s",e, exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat completion failed: {str(e)}"
        )