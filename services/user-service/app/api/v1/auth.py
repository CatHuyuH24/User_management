from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import timedelta, datetime

from core.database import get_db
from models.user import User
from schemas.user import UserCreate, UserLogin, UserCreateResponse, UserResponse, Token, UserRole, PasswordChange
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

@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user = Depends(get_current_active_user_dependency),
    db: Session = Depends(get_db)
):
    """
    Change user password.
    
    - **current_password**: Current password for verification
    - **new_password**: New password (must meet strength requirements)
    """
    try:
        # Verify current password
        if not auth_service.verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Check if new password is different from current
        if auth_service.verify_password(password_data.new_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from current password"
            )
        
        # Update password
        from core.security import get_password_hash
        new_hashed_password = get_password_hash(password_data.new_password)
        
        # Update in database
        current_user.hashed_password = new_hashed_password
        current_user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"Password changed successfully for user: {current_user.username}")
        return {"message": "Password updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error changing password for user {current_user.username}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )

@router.post("/password-reset")
async def request_password_reset(
    email_data: dict,
    db: Session = Depends(get_db)
):
    """
    Request password reset for a user.
    
    - **email**: Email address of the user requesting password reset
    """
    try:
        email = email_data.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Email is required"
            )
        
        # Validate email format
        if "@" not in email or "." not in email.split("@")[-1]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid email format"
            )
        
        # Check if user exists (but don't reveal if user exists for security)
        user = user_service.get_user_by_email(db, email)
        
        if user:
            # In a real system, you would:
            # 1. Generate a password reset token
            # 2. Store it in database with expiration
            # 3. Send email with reset link
            # For now, we'll just log it
            logger.info(f"Password reset requested for user: {email}")
            
            # Generate a mock reset token (in real system, store in DB)
            reset_token = auth_service.create_access_token(
                data={
                    "sub": str(user.id),
                    "email": user.email,
                    "type": "password_reset"
                },
                expires_delta=timedelta(hours=1)  # 1 hour expiry for reset tokens
            )
            
            # In a real system, send this token via email
            logger.info(f"Password reset token generated for {email}: {reset_token}")
        
        # Always return success for security (don't reveal if email exists)
        return {
            "message": "If the email address exists in our system, a password reset link has been sent."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing password reset request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process password reset request"
        )

@router.post("/password-reset/confirm")
async def confirm_password_reset(
    reset_data: dict,
    db: Session = Depends(get_db)
):
    """
    Confirm password reset with token.
    
    - **token**: Password reset token from email
    - **new_password**: New password
    """
    try:
        token = reset_data.get("token")
        new_password = reset_data.get("new_password")
        
        if not token or not new_password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Token and new password are required"
            )
        
        # Validate password strength
        user_service.validate_password_strength(new_password)
        
        # Verify reset token
        token_data = auth_service.verify_token(token, expected_type="password_reset")
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Get user
        user = db.query(User).filter(User.id == token_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update password
        hashed_password = auth_service.get_password_hash(new_password)
        user.hashed_password = hashed_password
        user.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Password reset completed for user: {user.email}")
        return {"message": "Password has been reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming password reset: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )

# Legacy function for backward compatibility
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get current authenticated user (legacy function)."""
    return auth_service.get_current_user(db, credentials)
