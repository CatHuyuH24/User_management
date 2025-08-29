from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any
from core.database import get_db
from services.auth_service import auth_service, get_current_active_user_dependency
from services.mfa_service import mfa_service
from models.user import User
from schemas.mfa import (
    MFASetupRequest, 
    MFASetupResponse, 
    MFAVerifyRequest, 
    MFAVerifyResponse,
    MFADisableRequest,
    BackupCodesResponse,
    MFAStatus
)
from schemas.user import Token
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/mfa", tags=["MFA Authentication"])

@router.post("/initiate", response_model=dict)
async def initiate_mfa_setup(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """
    Initiate MFA setup for new users.
    Returns QR code and secret for authenticator app setup.
    """
    try:
        # Check if user already has MFA enabled
        if current_user.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is already enabled for this user"
            )
        
        # Generate secret and QR code
        secret = mfa_service.generate_secret()
        qr_code = mfa_service.generate_qr_code(secret, current_user.email)
        
        return {
            "qr_code": qr_code,
            "secret_key": secret,
            "message": "Scan the QR code with your authenticator app, then verify with the generated code"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initiating MFA setup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate MFA setup"
        )

@router.post("/complete-setup")
async def complete_mfa_setup(
    secret_key: str,
    verification_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """
    Complete MFA setup by verifying the TOTP code.
    """
    try:
        # Verify the code with the provided secret
        if not mfa_service.verify_totp_code(secret_key, verification_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code. Please try again."
            )
        
        # Setup MFA for user
        mfa_response = mfa_service.setup_mfa_with_secret(db, current_user, secret_key, verification_code)
        
        # Enable MFA on user account
        current_user.mfa_enabled = True
        db.commit()
        
        return {
            "message": "MFA has been successfully enabled for your account",
            "backup_codes": mfa_response.backup_codes,
            "important": "Please save these backup codes in a secure location. They can be used to access your account if you lose your authenticator device."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying MFA setup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete MFA setup"
        )

@router.get("/status", response_model=MFAStatus)
async def get_mfa_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """Get MFA status for current user"""
    try:
        return mfa_service.get_mfa_status(db, current_user)
    except Exception as e:
        logger.error(f"Error getting MFA status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get MFA status"
        )

@router.post("/setup", response_model=MFASetupResponse)
async def setup_mfa(
    request: MFASetupRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """Setup MFA for current user"""
    try:
        # Check if user is verified
        if not current_user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email verification required before enabling MFA"
            )
        
        return mfa_service.setup_mfa(db, current_user, request.verification_code)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting up MFA: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to setup MFA"
        )

@router.post("/verify", response_model=MFAVerifyResponse)
async def verify_mfa(
    request: MFAVerifyRequest,
    db: Session = Depends(get_db)
):
    """Verify MFA code and complete authentication"""
    try:
        # Find user by email
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Verify MFA code
        if not mfa_service.verify_mfa_code(db, user, request.mfa_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA code"
            )
        
        # Create full access token
        access_token = auth_service.create_full_access_token(user)
        
        # Update user's last login
        user.last_login = db.execute("SELECT NOW()").scalar()
        user.login_count = (user.login_count or 0) + 1
        db.commit()
        
        return MFAVerifyResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=auth_service.access_token_expire_minutes * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying MFA: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify MFA"
        )

@router.post("/disable")
async def disable_mfa(
    request: MFADisableRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """Disable MFA for current user"""
    try:
        # Verify current password
        if not auth_service.verify_password(request.password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid password"
            )
        
        # Verify current MFA code
        if not mfa_service.verify_mfa_code(db, current_user, request.mfa_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA code"
            )
        
        # Disable MFA
        if not mfa_service.disable_mfa(db, current_user):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to disable MFA"
            )
        
        return {"message": "MFA has been disabled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling MFA: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable MFA"
        )

@router.post("/backup-codes/regenerate", response_model=BackupCodesResponse)
async def regenerate_backup_codes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """Regenerate backup codes for current user"""
    try:
        backup_codes = mfa_service.regenerate_backup_codes(db, current_user)
        
        return BackupCodesResponse(backup_codes=backup_codes)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating backup codes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to regenerate backup codes"
        )

@router.get("/qr-code")
async def get_mfa_qr_code(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """Get QR code for MFA setup (for existing users who want to set up on a new device)"""
    try:
        # Check if user has MFA enabled
        if not current_user.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is not enabled for this user"
            )
        
        # Get MFA secret
        from models.mfa import MFASecret
        mfa_secret = db.query(MFASecret).filter(
            MFASecret.user_id == current_user.id,
            MFASecret.is_active == True
        ).first()
        
        if not mfa_secret:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MFA secret not found"
            )
        
        # Generate QR code
        qr_code = mfa_service.generate_qr_code(mfa_secret.secret_key, current_user.email)
        
        return {
            "qr_code": qr_code,
            "secret_key": mfa_secret.secret_key,
            "backup_codes_count": mfa_secret.backup_codes_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting QR code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get QR code"
        )

# Rate limiting for MFA endpoints
from functools import wraps
from time import time
import redis
import json

# Simple in-memory rate limiting (in production, use Redis)
mfa_attempts = {}

def rate_limit_mfa(max_attempts: int = 5, window_minutes: int = 15):
    """Rate limiting decorator for MFA endpoints"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get client IP from request
            request = kwargs.get('request') or args[0] if args else None
            if not request:
                return await func(*args, **kwargs)
            
            client_ip = request.client.host
            current_time = time()
            window_seconds = window_minutes * 60
            
            # Clean old attempts
            if client_ip in mfa_attempts:
                mfa_attempts[client_ip] = [
                    attempt_time for attempt_time in mfa_attempts[client_ip]
                    if current_time - attempt_time < window_seconds
                ]
            
            # Check rate limit
            if client_ip in mfa_attempts and len(mfa_attempts[client_ip]) >= max_attempts:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Too many MFA attempts. Try again in {window_minutes} minutes."
                )
            
            try:
                result = await func(*args, **kwargs)
                return result
            except HTTPException as e:
                # Record failed attempt
                if e.status_code == status.HTTP_401_UNAUTHORIZED:
                    if client_ip not in mfa_attempts:
                        mfa_attempts[client_ip] = []
                    mfa_attempts[client_ip].append(current_time)
                raise
        
        return wrapper
    return decorator

# Apply rate limiting to sensitive endpoints
verify_mfa = rate_limit_mfa()(verify_mfa)
