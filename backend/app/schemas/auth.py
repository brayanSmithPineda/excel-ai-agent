from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class SignupRequest(LoginRequest):
    full_name: str
    company: Optional[str] = None

class AuthResponse(BaseModel):
    user_id: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    user_metadata: dict = {}
    access_token: str #JWT token
    refresh_token: str #Supabase refresh token, this is used to refresh the access token and keep the user logged in
    token_type: str = "Bearer"

class ErrorResponse(BaseModel):
    error: str 
    message: str
    detail: Optional[str] = None

class UserProfile(BaseModel):
    user_id: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str
    user_metadata: dict = {}

class LogoutResponse(BaseModel):
    message: str

class RefreshRequest(BaseModel):
    refresh_token: str