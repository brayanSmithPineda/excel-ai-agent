from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.auth import LoginRequest, LogoutResponse, SignupRequest, AuthResponse, ErrorResponse, UserProfile, LogoutResponse, RefreshRequest
from app.config.database import get_supabase_client
from app.auth.dependencies import get_current_user
from typing import Dict, Any



router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest) -> AuthResponse:
    try:
        supabase = get_supabase_client() #this client help us to interact with the supabase database
        response = supabase.auth.sign_in_with_password(
            {
                "email": request.email,
                "password": request.password
            }
        )

        if response.user and response.session:
            return AuthResponse(
                user_id=response.user.id,
                email=response.user.email,
                full_name=response.user.user_metadata.get("full_name") or response.user.email.split("@")[0],
                role=response.user.role or "authenticated",
                user_metadata=response.user.user_metadata,
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                token_type="Bearer"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
    except Exception as e:
        if "invalid" in str(e).lower() or "credentials" in str(e).lower():
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid email or password"
            )
        else:
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = "Authenticated service tempoary unavailable"
            )

@router.post("/signup", response_model=AuthResponse)
async def signup(request: SignupRequest) -> AuthResponse:
    try:
        supabase = get_supabase_client()
        response = supabase.auth.sign_up(
            {
                "email": request.email,
                "password": request.password,
                "options": {
                    "data": {
                        "full_name": request.full_name,
                        "company": request.company
                    }
                }
            }
        )
        
        if response.user and response.session:
            return AuthResponse(
                user_id=response.user.id,
                email=response.user.email,
                full_name=response.user.user_metadata.get("full_name") or response.user.email.split("@")[0],
                role=response.user.role or "authenticated",
                user_metadata=response.user.user_metadata,
                access_token=response.session.access_token,
                refresh_token=response.session.refresh_token,
                token_type="Bearer"
            )
        elif response.user and not response.session:
            raise HTTPException(
                status_code=status.HTTP_201_CREATED,
                detail="User created successfully. Please check your email to confirm your account."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
    except Exception as e:
        error_msg = str(e).lower()
        if "already registered" in error_msg:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = "Email already registered"
            )
        elif "invalid" in error_msg or "email" in error_msg:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Invalid email or password"
            )
        else:
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = "Authenticated service tempoary unavailable"
            )
        
@router.get("/me", response_model = UserProfile)
async def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)) -> UserProfile:
    return UserProfile(
        user_id=current_user["user_id"],
        email=current_user["email"],
        full_name=current_user["user_metadata"].get("full_name") or current_user["email"].split("@")[0],
        role=current_user["role"],
        user_metadata=current_user["user_metadata"],
    )   

@router.post("/logout", response_model=LogoutResponse)
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)) -> LogoutResponse:
    try:
        supabase = get_supabase_client()
        supabase.auth.sign_out()
        return LogoutResponse(message="Logged out successfully")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout"
        )

@router.post("/refresh", response_model=AuthResponse)
async def refresh(request: RefreshRequest) -> AuthResponse:
    try:
        
        supabase = get_supabase_client()
        response = supabase.auth.refresh_session(request.refresh_token)

        return AuthResponse(
            user_id=response.user.id,
            email=response.user.email,
            full_name=response.user.user_metadata.get("full_name") or response.user.email.split("@")[0],
            role=response.user.role or "authenticated",
            user_metadata=response.user.user_metadata,
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token,
            token_type="Bearer"
        )
    except Exception as e:
        print(f"DEBUG: Refresh error: {str(e)}")
        print(f"DEBUG: Error type: {type(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Refresh failed: {str(e)}"  # Show actual error temporarily
        )