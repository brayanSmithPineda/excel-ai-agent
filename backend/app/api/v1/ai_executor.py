"""
AI Executor API Router

Handles AI code generation and execution requests.
Allows users to upload Excel files and request AI operations.
"""
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from typing import Dict, Any, List, Optional
from pathlib import Path
import tempfile
import base64
import uuid  # For generating unique request IDs
from loguru import logger

# Import authentication
from app.auth.dependencies import get_current_user

# Import schemas
from app.schemas.ai_executor import (
    ExecuteTaskRequest,
    ExecuteTaskResponse,
    PermissionRequiredResponse,
    ExecutionErrorResponse
)

# Import AI Executor service
from app.services.ai_executor.executor import AICodeExecutor


# Create router with prefix and tags
router = APIRouter(prefix="/ai-executor", tags=["AI Code Executor"])


@router.post("/execute-task")
async def execute_task(
    # Form data (user request and operation type)
    user_request: str = Form(..., description="Natural language request from user"),
    operation_type: Optional[str] = Form(None, description="Optional operation type hint"),
    
    # File uploads (list of Excel files)
    files: List[UploadFile] = File(default=[], description="Optional Excel files to process"),
    
    # Authentication (get current user from JWT token)
    current_user: Dict[str, Any] = Depends(get_current_user)  # ✅ Enable JWT validation

):
    """
    Execute an AI task with uploaded files.
    
    Flow:
    1. User uploads Excel files and provides natural language request
    2. Save uploaded files temporarily
    3. Initialize AICodeExecutor with user_id
    4. Execute task (AI generates code → validates → executes in Docker)
    5. Return results or permission request
    
    Args:
        user_request: Natural language request (e.g., "Stack these workbooks")
        operation_type: Optional hint about operation (e.g., "consolidate")
        files: List of uploaded Excel files
        current_user: Authenticated user info from JWT token
    
    Returns:
        ExecuteTaskResponse: Successful execution results
        OR
        PermissionRequiredResponse: MEDIUM_RISK permission request
        OR
        ExecutionErrorResponse: Execution failed or blocked
    """
    try:
        # Log the request
        user_id = current_user.get("sub") or current_user.get("user_id")
        logger.info(f"🚀 AI Executor request from user {user_id}: {user_request}")
        logger.info(f"📁 Files uploaded: {len(files)}")

        # Step 1: Create unique directories for this request (prevents race conditions)
        request_id = str(uuid.uuid4())  # Generate unique ID for this request
        base_dir = Path("/tmp/ai-executor") / request_id
        input_dir = base_dir / "input"
        output_dir = base_dir / "output"

        # Create the unique directories (parents=True creates all parent directories)
        input_dir.mkdir(parents=True, exist_ok=True)
        output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"📂 Created unique workspace: {base_dir}")

        # Step 2: Save uploaded files to temporary directory
        temp_files = []

        try:
            if files:
                for uploaded_file in files:
                    # Save file to tmp/input directory
                    file_path = input_dir / uploaded_file.filename

                    # Read and write file
                    content = await uploaded_file.read()
                    with open(file_path, 'wb') as f:
                        f.write(content)

                    temp_files.append(file_path)
                    logger.info(f"✅ Saved: {uploaded_file.filename} ({len(content)} bytes)")

            # Step 3: Initialize AI Executor with authenticated user_id
            executor = AICodeExecutor(user_id=user_id)

            # Step 4: Execute the task
            logger.info(f"⚙️ Executing task with {len(temp_files)} file(s)...")
            result = await executor.execute_task(
                user_request=user_request,
                uploaded_files=temp_files,
                operation_type=operation_type
            )

            # Step 5: Handle different response types

            # Case 1: MEDIUM_RISK - Permission required
            if result.get("requires_permission"):
                logger.warning(f"⚠️ MEDIUM_RISK permission required for user {user_id}")
                return PermissionRequiredResponse(**result)

            # Case 2: Execution failed or blocked
            if not result.get("success"):
                logger.error(f"❌ Execution failed for user {user_id}: {result.get('error')}")
                return ExecutionErrorResponse(**result)

            # Case 3: Success - encode output files to base64
            response_data = {
                "success": True,
                "output": result.get("output"),
                "exit_code": result.get("exit_code")
            }

            # Encode output files to base64 for JSON transport
            if result.get("output_files"):
                encoded_files = {}
                for filename, file_bytes in result["output_files"].items():
                    encoded_files[filename] = base64.b64encode(file_bytes).decode('utf-8')
                response_data["output_files"] = encoded_files
                logger.info(f"📦 Returning {len(encoded_files)} output file(s)")

            logger.info(f"✅ Task completed successfully for user {user_id}")
            return ExecuteTaskResponse(**response_data)

        finally:
            # Cleanup: Delete entire unique workspace directory
            try:
                import shutil
                if base_dir.exists():
                    shutil.rmtree(base_dir)  # Remove entire directory tree
                    logger.info(f"🧹 Cleaned up workspace: {base_dir}")
            except Exception as e:
                logger.warning(f"⚠️ Cleanup warning: {e}")

    except HTTPException:
        # Re-raise HTTP exceptions (validation errors, etc.)
        raise

    except Exception as e:
        # Catch any unexpected errors
        logger.error(f"💥 Unexpected error in execute_task: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/health")
async def ai_executor_health():
    """
    Health check endpoint for AI Executor service.
    
    Verifies that the AI Executor service is operational.
    """
    return {
        "status": "healthy",
        "service": "AI Code Executor",
        "message": "AI Executor service is running"
    }
