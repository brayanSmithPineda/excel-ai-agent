from functools import lru_cache #This ensure settings are cached and only loaded once for performance
from typing import List, Optional #This is used to type hint the settings, List is a list of strings, Optional is a string or None
from pydantic import SecretStr, validator #This is used to validate the settings
from pydantic_settings import BaseSettings #This is used to create the settings class
import os #This is used to get the environment variables

class Settings(BaseSettings): #BaseSettings is a class that provides the basic functionality for settings, it is a subclass of BaseModel
    """
    Application settings loaded from environment variables.
    Uses Pydantic to validate and SecretStr to store sensitive information.
    """
    #Environment Configuration
    environment: str = 'development' # environment is a string that is set to development by default
    debug: bool = True #Debug true means the logs are verbose, False means only errors are logged
    project_name: str = 'Excel AI Agent Backend'
    api_v1_str: str = '/api/v1' #This is the API version string, API of our application excel-ai-agent

    #Supabase Configuration
    supabase_url: str
    supabase_project_id: str
    supabase_anon_key: SecretStr 
    supabase_service_role_key: SecretStr

    #Database Configuration
    database_url: str

    #Security Configuration
    jwt_secret_key: SecretStr
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 60

    #AI Configuration
    gemini_api_key: Optional[SecretStr] = None

    #CORS Configuration for Excel Add-In, origins that can communicate with the API
    allowed_origins: List[str] = [
          "https://localhost:3000", #Development
          "https://excel.office.com", #Excel on the web
          "https://excel.officeapps.live.com" #Excel online
      ]

    @validator("allowed_origins", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list format"""
        if isinstance(v, str):
            # Handle JSON-like string format from .env
            v = v.strip('[]').replace('"', '').split(',')
            return [origin.strip() for origin in v]
        return v

    @validator("environment")
    def validate_environment(cls, v):
        """Ensure environment is one of the allowed values"""
        allowed_environments = ["development", "staging", "production"]
        if v not in allowed_environments:
            raise ValueError(f"Environment must be one of: {allowed_environments}")
        return v

    #Config class is used to configure the settings, it is a subclass of BaseSettings
    #Pydantic will use this class to load the settings from the .env file, without this class i will need to export each variable manually
    class Config:
        # Load from .env file
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Make environment variable names case-insensitive
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """
    Get the application settings.
    Uses lru_cache to cache the settings for performance.
    """
    return Settings()

#Create setting instance
settings = get_settings()