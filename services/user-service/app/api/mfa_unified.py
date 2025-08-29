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
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/mfa", tags=["Multi-Factor Authentication"])

# ========== MFA Setup Flow ==========

@router.post("/setup/initiate", response_model=dict)
async def initiate_mfa_setup(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """
    Step 1: Initiate MFA setup for users.
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

@router.post("/setup/complete", response_model=MFASetupResponse)
async def complete_mfa_setup(
    secret_key: str,
    verification_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """
    Step 2: Complete MFA setup by verifying the TOTP code.
    """
    try:
        # Check if user already has MFA enabled
        if current_user.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is already enabled for this user"
            )
        
        # Verify the TOTP code with the secret
        if not mfa_service.verify_totp_code(secret_key, verification_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )
        
        # Enable MFA for the user
        result = mfa_service.enable_mfa(db, current_user, secret_key)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing MFA setup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete MFA setup"
        )

# ========== MFA Status and Management ==========

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
        
        # Disable MFA
        mfa_service.disable_mfa(db, current_user)
        
        return {"message": "MFA has been disabled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling MFA: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to disable MFA"
        )

# ========== MFA Verification (Login Flow) ==========

@router.post("/verify", response_model=Token)
async def verify_mfa_login(
    request: MFAVerifyRequest,
    db: Session = Depends(get_db)
):
    """
    Verify MFA code during login process.
    This endpoint is used after the user has provided username/password 
    and received an MFA token that needs to be verified.
    """
    try:
        # Extract user information from the MFA token
        payload = auth_service.verify_mfa_token(request.mfa_token)
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA token"
            )
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
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
        user.last_login = datetime.utcnow()
        user.login_count = (user.login_count or 0) + 1
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
        logger.error(f"Error verifying MFA: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify MFA"
        )

# ========== Backup Codes Management ==========

@router.post("/backup-codes/regenerate", response_model=BackupCodesResponse)
async def regenerate_backup_codes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """Regenerate backup codes for MFA recovery"""
    try:
        # Check if MFA is enabled
        if not current_user.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is not enabled for this user"
            )
        
        # Regenerate backup codes
        backup_codes = mfa_service.regenerate_backup_codes(db, current_user)
        
        return BackupCodesResponse(
            backup_codes=backup_codes,
            message="New backup codes generated successfully. Save these codes in a secure location."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating backup codes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to regenerate backup codes"
        )

@router.get("/qr-code")
async def get_qr_code(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """Get QR code for current MFA secret (for re-setup)"""
    try:
        # Check if MFA is enabled
        if not current_user.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA is not enabled for this user"
            )
        
        # Get current MFA secret and generate QR code
        mfa_secret = mfa_service.get_user_mfa_secret(db, current_user)
        if not mfa_secret:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="MFA secret not found"
            )
        
        qr_code = mfa_service.generate_qr_code(mfa_secret.secret_key, current_user.email)
        
        return {
            "qr_code": qr_code,
            "message": "QR code for current MFA secret"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting QR code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get QR code"
        )

# ========== Legacy Endpoints (for backward compatibility) ==========

@router.post("/setup", response_model=MFASetupResponse)
async def setup_mfa_legacy(
    request: MFASetupRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """
    Legacy MFA setup endpoint - redirects to new flow
    DEPRECATED: Use /setup/initiate and /setup/complete instead
    """
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

# ========== Alias endpoints for backward compatibility ==========

# These endpoints provide aliases for the main endpoints to maintain compatibility
@router.post("/initiate", response_model=dict)
async def initiate_mfa_alias(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """Alias for /setup/initiate - for backward compatibility"""
    return await initiate_mfa_setup(db, current_user)

@router.post("/complete-setup", response_model=MFASetupResponse)
async def complete_setup_alias(
    secret_key: str,
    verification_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """Alias for /setup/complete - for backward compatibility"""
    return await complete_mfa_setup(secret_key, verification_code, db, current_user)
