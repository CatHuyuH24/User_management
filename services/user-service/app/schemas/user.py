from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
import re

class UserRole(str, Enum):
    CLIENT = "client"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

# Schema for user creation (signup)
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username must be 3-50 characters")
    email: EmailStr = Field(..., description="Valid email address required")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    role: Optional[UserRole] = Field(UserRole.CLIENT, description="User role")
    
    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers, and underscores')
        return v.lower()
    
    @validator('password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

# Schema for user login (now includes MFA flow)
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Schema for MFA verification
class MFAVerify(BaseModel):
    email: EmailStr
    mfa_code: str = Field(..., min_length=6, max_length=6, description="6-digit MFA code")

# Schema for MFA setup
class MFASetup(BaseModel):
    verification_code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")

# Schema for user response (public data)
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    is_verified: bool
    role: UserRole
    mfa_enabled: bool
    created_at: datetime
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    year_of_birth: Optional[int] = None
    description: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True

# Schema for user profile update
class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    year_of_birth: Optional[int] = Field(None, ge=1900, le=2024)
    description: Optional[str] = Field(None, max_length=1000)
    avatar_url: Optional[str] = Field(None, max_length=500, description="URL or path to user's avatar image")

# Schema for password change
class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_new_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

# Schema for JWT token response
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    mfa_required: Optional[bool] = False

# Schema for token payload
class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    role: Optional[UserRole] = None
    email: Optional[str] = None

# Schema for signup response
class UserCreateResponse(BaseModel):
    message: str
    user: UserResponse
    verification_required: bool = True

# Schema for MFA setup response
class MFASetupResponse(BaseModel):
    qr_code: str  # Base64 encoded QR code image
    secret_key: str  # For manual entry
    backup_codes: List[str]

# Schema for backup codes
class BackupCodes(BaseModel):
    codes: List[str] = Field(..., description="List of backup codes")

# Schema for email verification
class EmailVerificationRequest(BaseModel):
    email: EmailStr

# Schema for error responses
class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
