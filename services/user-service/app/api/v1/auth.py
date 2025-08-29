from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import timedelta, datetime

from core.database import get_db
from schemas.user import UserCreate, UserLogin, UserCreateResponse, UserResponse, Token, UserRole
from services.user_service import user_service
from services.auth_service import auth_service, get_current_active_user_dependency
from services.mfa_service import mfa_service
from core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

@router.post("/signup", response_model=UserCreateResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_create: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    - **username**: Unique username (3-50 characters, alphanumeric + underscore)
    - **email**: Valid email address
    - **password**: Strong password (min 8 chars, uppercase, lowercase, digit, special char)
    - **first_name**: Optional first name
    - **last_name**: Optional last name
    - **role**: User role (default: client)
    """
    try:
        # Create user
        user = user_service.create_user(db, user_create)
        
        # Return user data (excluding sensitive information)
        user_response = UserResponse.model_validate(user)
        
        return UserCreateResponse(
            message="User created successfully. Please complete MFA setup on first login for enhanced security.",
            user=user_response,
            verification_required=True,  # Email verification
            mfa_setup_required=True      # MFA setup required
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during user creation"
        )

@router.post("/login", response_model=Token)
async def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token.
    For users with MFA enabled, returns a temporary token requiring MFA verification.
    
    - **username** or **email**: Username or registered email address
    - **password**: User password
    """
    try:
        # Determine if the login identifier is an email or username
        login_identifier = user_login.email if user_login.email else user_login.username
        
        if not login_identifier:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either username or email must be provided",
            )
        
        # Authenticate user using flexible method
        user = auth_service.authenticate_user_flexible(db, login_identifier, user_login.password)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username/email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Skip email verification requirement for now
        # if not user.is_verified:
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail="Please verify your email address before logging in",
        #     )
        
        # Check if MFA is enabled
        if user.mfa_enabled:
            # Create temporary MFA token
            mfa_token = auth_service.create_mfa_token(user.id, user.email)
            
            return Token(
                access_token=mfa_token,
                token_type="bearer",
                expires_in=auth_service.mfa_token_expire_minutes * 60,
                mfa_required=True
            )
        
        # Create full access token for users without MFA
        access_token = auth_service.create_full_access_token(user)
        
        # Update user's last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=auth_service.access_token_expire_minutes * 60,
            mfa_required=False
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication"
        )

@router.post("/refresh", response_model=Token)
async def refresh_token(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user_dependency)
):
    """
    Refresh access token for authenticated user.
    """
    try:
        new_token = auth_service.refresh_token(db, current_user)
        
        return Token(
            access_token=new_token,
            token_type="bearer",
            expires_in=auth_service.access_token_expire_minutes * 60
        )
    except Exception as e:
        logger.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user = Depends(get_current_active_user_dependency)
):
    """Get current authenticated user information."""
    return UserResponse.model_validate(current_user)

@router.post("/logout")
async def logout():
    """
    Logout endpoint (client-side token invalidation).
    In a production environment, you might want to implement token blacklisting.
    """
    return {"message": "Successfully logged out"}

# Legacy function for backward compatibility
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user (legacy function)."""
    return auth_service.get_current_user(db, credentials)
