from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "User Management Service"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@db:5432/db"
    
    # Security
    SECRET_KEY: str = "a-very-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Password Security
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True
    PASSWORD_REQUIRE_DIGITS: bool = True
    PASSWORD_REQUIRE_SPECIAL: bool = True
    
    # Rate Limiting (Increased for testing)
    SIGNUP_RATE_LIMIT: int = 100  # per hour per IP (increased for testing)
    LOGIN_RATE_LIMIT: int = 200  # per hour per IP (increased for testing)
    API_RATE_LIMIT: int = 1000  # per hour per IP (added general API rate limit)
    
    # Email Configuration (for future email verification)
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = ""
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    
    # File Upload
    MAX_AVATAR_SIZE_MB: int = 5
    ALLOWED_AVATAR_EXTENSIONS: list = [".jpg", ".jpeg", ".png", ".gif"]
    AVATAR_UPLOAD_PATH: str = "/app/uploads/avatars"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
