"""
Pydantic schemas for AI Executor API endpoints.

These schemas define the request/response structure for AI code execution.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ExecuteTaskRequest(BaseModel):
    """
    Request schema for executing an AI task.
    
    The user provides a natural language request, and files are uploaded separately.
    """
    user_request: str = Field( #Field() is used to define the field and its attributes
        ..., #... means required no default value
        description="Natural language request from user (e.g., 'Stack these workbooks')", #show in api docs
        min_length=1,
        max_length=1000
    )
    operation_type: Optional[str] = Field(
        None,
        description="Optional hint about operation type (e.g., 'consolidate', 'pivot', 'filter')"
    )


class ExecuteTaskResponse(BaseModel):
    """
    Response schema for successful task execution.
    
    Returns the execution results and any generated output files.
    """
    success: bool = Field(..., description="Whether execution succeeded")
    output: Optional[str] = Field(None, description="Standard output from code execution")
    output_files: Optional[Dict[str, str]] = Field(
        None,
        description="Generated files as {filename: base64_encoded_content}"
    )
    exit_code: Optional[int] = Field(None, description="Execution exit code (0 = success)")
    execution_time_ms: Optional[int] = Field(None, description="Execution time in milliseconds")


class PermissionRequiredResponse(BaseModel):
    """
    Response when MEDIUM_RISK code requires user permission.
    
    Contains details about why permission is needed and what will execute.
    """
    success: bool = Field(False, description="Always False when permission required")
    requires_permission: bool = Field(True, description="Always True for this response")
    risk_level: str = Field("medium", description="Risk level: 'medium'")
    explanation: str = Field(..., description="User-friendly explanation of why permission needed")
    restricted_imports: List[str] = Field(..., description="List of imports requiring permission")
    code_preview: str = Field(..., description="The actual code that will execute if approved")
    message: str = Field(..., description="Message to display to user")


class ExecutionErrorResponse(BaseModel):
    """
    Response when execution fails or is blocked.
    
    Contains error details and helpful debugging information.
    """
    success: bool = Field(False, description="Always False for errors")
    error: str = Field(..., description="Main error message")
    reason: Optional[str] = Field(None, description="Detailed reason for failure (HIGH_RISK blocks)")
    details: Optional[str] = Field(None, description="Additional error details (stack traces, etc.)")
    output: Optional[str] = Field(None, description="Any output before failure")