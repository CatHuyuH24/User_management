import pyotp
import qrcode
import io
import base64
import secrets
import string
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.user import User
from models.mfa import MFASecret
from schemas.mfa import MFASetupResponse, MFAStatus
from core.config import settings
import logging

logger = logging.getLogger(__name__)

class MFAService:
    """Service for handling Multi-Factor Authentication operations"""
    
    def __init__(self):
        self.issuer_name = getattr(settings, 'APP_NAME', 'User Management System')
        
    def generate_secret(self) -> str:
        """Generate a new TOTP secret key"""
        return pyotp.random_base32()
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for MFA"""
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric codes
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) 
                          for _ in range(8))
            codes.append(code)
        return codes
    
    def generate_qr_code(self, secret: str, user_email: str) -> str:
        """Generate QR code for TOTP setup"""
        try:
            # Create TOTP URI
            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=user_email,
                issuer_name=self.issuer_name
            )
            
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(totp_uri)
            qr.make(fit=True)
            
            # Create QR code image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"Error generating QR code: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate QR code"
            )
    
    def verify_totp_code(self, secret: str, code: str, window: int = 1) -> bool:
        """Verify TOTP code with tolerance window"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(code, valid_window=window)
        except Exception as e:
            logger.error(f"Error verifying TOTP code: {str(e)}")
            return False
    
    def verify_backup_code(self, db: Session, user_id: int, code: str) -> bool:
        """Verify backup code and mark as used"""
        try:
            mfa_secret = db.query(MFASecret).filter(
                MFASecret.user_id == user_id,
                MFASecret.is_active == True
            ).first()
            
            if not mfa_secret or not mfa_secret.backup_codes:
                return False
            
            backup_codes = mfa_secret.backup_codes.split(',')
            code_upper = code.upper()
            
            if code_upper in backup_codes:
                # Remove used backup code
                backup_codes.remove(code_upper)
                mfa_secret.backup_codes = ','.join(backup_codes)
                mfa_secret.backup_codes_count = len(backup_codes)
                db.commit()
                
                logger.info(f"Backup code used for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verifying backup code: {str(e)}")
            db.rollback()
            return False
    
    def setup_mfa(self, db: Session, user: User, verification_code: str) -> MFASetupResponse:
        """Setup MFA for a user"""
        try:
            # Check if user already has MFA enabled
            existing_mfa = db.query(MFASecret).filter(
                MFASecret.user_id == user.id,
                MFASecret.is_active == True
            ).first()
            
            if existing_mfa:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="MFA is already enabled for this user"
                )
            
            # Generate new secret and verify the provided code
            secret = self.generate_secret()
            
            if not self.verify_totp_code(secret, verification_code):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid verification code"
                )
            
            # Generate backup codes
            backup_codes = self.generate_backup_codes()
            
            # Create MFA secret record
            mfa_secret = MFASecret(
                user_id=user.id,
                secret_key=secret,
                backup_codes=','.join(backup_codes),
                backup_codes_count=len(backup_codes),
                is_active=True
            )
            
            db.add(mfa_secret)
            
            # Enable MFA for user
            user.mfa_enabled = True
            
            db.commit()
            
            # Generate QR code
            qr_code = self.generate_qr_code(secret, user.email)
            
            logger.info(f"MFA setup completed for user {user.id}")
            
            return MFASetupResponse(
                qr_code=qr_code,
                secret_key=secret,
                backup_codes=backup_codes
            )
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Error setting up MFA: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to setup MFA"
            )
    
    def verify_mfa_code(self, db: Session, user: User, code: str) -> bool:
        """Verify MFA code (TOTP or backup code)"""
        try:
            if not user.mfa_enabled:
                return False
            
            mfa_secret = db.query(MFASecret).filter(
                MFASecret.user_id == user.id,
                MFASecret.is_active == True
            ).first()
            
            if not mfa_secret:
                return False
            
            # Try TOTP first
            if self.verify_totp_code(mfa_secret.secret_key, code):
                # Update last used timestamp
                mfa_secret.last_used_at = db.execute("SELECT NOW()").scalar()
                db.commit()
                return True
            
            # Try backup code
            if len(code) == 8 and self.verify_backup_code(db, user.id, code):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verifying MFA code: {str(e)}")
            return False
    
    def disable_mfa(self, db: Session, user: User) -> bool:
        """Disable MFA for a user"""
        try:
            # Deactivate MFA secret
            mfa_secret = db.query(MFASecret).filter(
                MFASecret.user_id == user.id,
                MFASecret.is_active == True
            ).first()
            
            if mfa_secret:
                mfa_secret.is_active = False
            
            # Disable MFA for user
            user.mfa_enabled = False
            
            db.commit()
            
            logger.info(f"MFA disabled for user {user.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error disabling MFA: {str(e)}")
            db.rollback()
            return False
    
    def regenerate_backup_codes(self, db: Session, user: User) -> List[str]:
        """Regenerate backup codes for a user"""
        try:
            if not user.mfa_enabled:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="MFA is not enabled for this user"
                )
            
            mfa_secret = db.query(MFASecret).filter(
                MFASecret.user_id == user.id,
                MFASecret.is_active == True
            ).first()
            
            if not mfa_secret:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="MFA secret not found"
                )
            
            # Generate new backup codes
            backup_codes = self.generate_backup_codes()
            
            # Update MFA secret
            mfa_secret.backup_codes = ','.join(backup_codes)
            mfa_secret.backup_codes_count = len(backup_codes)
            
            db.commit()
            
            logger.info(f"Backup codes regenerated for user {user.id}")
            return backup_codes
            
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            logger.error(f"Error regenerating backup codes: {str(e)}")
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to regenerate backup codes"
            )
    
    def get_mfa_status(self, db: Session, user: User) -> MFAStatus:
        """Get MFA status for a user"""
        try:
            if not user.mfa_enabled:
                return MFAStatus(
                    enabled=False,
                    secret_exists=False,
                    backup_codes_count=0,
                    last_used=None
                )
            
            mfa_secret = db.query(MFASecret).filter(
                MFASecret.user_id == user.id,
                MFASecret.is_active == True
            ).first()
            
            if not mfa_secret:
                return MFAStatus(
                    enabled=False,
                    secret_exists=False,
                    backup_codes_count=0,
                    last_used=None
                )
            
            return MFAStatus(
                enabled=True,
                secret_exists=bool(mfa_secret.secret_key),
                backup_codes_count=mfa_secret.backup_codes_count or 0,
                last_used=mfa_secret.last_used_at
            )
            
        except Exception as e:
            logger.error(f"Error getting MFA status: {str(e)}")
            return MFAStatus(
                enabled=False,
                secret_exists=False,
                backup_codes_count=0,
                last_used=None
            )

# Create singleton instance
mfa_service = MFAService()
