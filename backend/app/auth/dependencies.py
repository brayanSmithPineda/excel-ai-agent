"""
This module provides FastAPI  dependency functions for user authentication and authorization.
Key features:
- Extract JWT tokens from authorization headers
- Validate tokens and return user information
- Provide optional authentication for public routes
- Role-based access control
- Graceful handling of authentication failures
"""
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException
from typing import Dict, Any, Optional
from app.auth.jwt_handler import jwt_handler
from fastapi import status
# This tells FastAPI to look for Authorization header with Bearer token
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Get the current authenticated user from the JWT token.
    Args:
        credentials (HTTPAuthorizationCredentials): The HTTP authorization credentials
    Returns:
        Dict[str, Any]: The user information extracted from the token
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header with Bearer token required",
            headers={"WWW-Authenticate": "Bearer"}
        )
    token = credentials.credentials

    user_info = jwt_handler.extract_user_info(token)
    return user_info

async def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str,Any]]:
    """
    Similar to get_current_user, but returns None if no credentials are provided
    useful for public routes that work for both authenticated and unauthenticated users
    """
    if not credentials:
        return None
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None

def require_role(required_role: str):
    """
    Create a dependency function that checks if the user has the required role
    """
    async def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        """
        check if the user has the required role
        """
        user_role = current_user.get("role", "authenticated")
        if user_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User does not have the required role: {required_role}, your role is: {user_role}"
            )
        return current_user
    return role_checker

def require_any_role(*allowed_roles: str):
    """
    Create a dependency function that checks if the user has any of the allowed roles
    """
    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_user)
    ) -> Dict[str, Any]:
        user_role = current_user.get("role", "authenticated")

        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {allowed_roles}, your role: '{user_role}'"
            )

        return current_user

    return role_checker

require_admin = require_role("admin")
require_super_admin = require_role("super_admin")
require_staff = require_any_role("admin", "super_admin", "moderator")