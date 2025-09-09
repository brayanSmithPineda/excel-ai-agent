"""
JWT token validations for supabase authentication

key responsabilities:
- Decode and validate JWT toekns using Supabase's JWT secret. This JWT tokens are generated when users log in to the application.
- Extract user information (ID, email, role) from validated tokens.
- Handle token expirations and validation errors.
- Provide secure  user authentication for FastAPI routes.
"""
from app.config.settings import settings
from typing import Dict, Any, Optional
import jwt #This is the library that we use to decode and validate JWT tokens
from fastapi import HTTPException, status

class JWTHandler:
    def __init__(self):
        self.jwt_secret = settings.jwt_secret_key.get_secret_value() #get_secre_value() is method associated with SecretStr class, it returns the secret value of the JWT secret key
        self.algorithm = settings.jwt_algorithm

        self.supabase_url = settings.supabase_url
        self.project_id = settings.supabase_project_id
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """
            Decode and validate a JWT token from Supabase.    
            Args:
                token (str): The JWT token to decode and validate
            Returns:
                Dict[str, Any]: The decoded token payload with user information
            Raises:
                HTTPException: If token is invalid, expired, or malformed
            Obs: Decode means to extract the information from the token and validate it againt Supabase's JWT secret.   
        """

        try:
            #decode the token using the jwt library, it uses the JWT secret from supabase to later validate it
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.algorithm],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iat": True,
                    "verify_aud": True,
                }
            )

            #validate the token using the supabase library
            expected_issuer = f"https://{self.project_id}.supabase.co/auth/v1"
            if payload.get("iss") != expected_issuer:
                raise HTTPException(
                    status_code = status.HTTP_401_UNAUTHORIZED,
                    detail = "Invalid token issuer - not from supabase"
                )
            return payload
        except jwt.ExpiredSignatureError as e:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = f"Invalid authentication token: {str(e)}"
            )
    def extract_user_info(self, token: str) -> Dict[str, Any]:
        """
        Extract user information from a validated JWT token.
        Args:
            token (str): The JWT token to extract user information from
        Returns:
            Dict[str, Any]: The user information extracted from the token
        """
        payload = self.decode_token(token)

        user_info = {
            "user_id": payload.get("sub"),           # User ID from Supabase Auth
            "email": payload.get("email"),           # User's email address
            "role": payload.get("role", "authenticated"),  # User role (default: authenticated)
            "aud": payload.get("aud"),               # Token audience
            "exp": payload.get("exp"),               # Expiration timestamp
            "iat": payload.get("iat"),               # Issued at timestamp
            "app_metadata": payload.get("app_metadata", {}),     # App-specific metadata
            "user_metadata": payload.get("user_metadata", {}),
        }

        # Validate that required user information is present
        if not user_info["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing user ID - invalid authentication token"
            )

        if not user_info["email"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing email - invalid authentication token"
            )

        return user_info

jwt_handler = JWTHandler()