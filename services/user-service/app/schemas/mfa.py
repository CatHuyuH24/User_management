from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class MFASecretCreate(BaseModel):
    secret_key: str = Field(..., description="TOTP secret key")
    
class MFASetupRequest(BaseModel):
    verification_code: str = Field(..., min_length=6, max_length=6, description="6-digit verification code")

class MFASetupResponse(BaseModel):
    qr_code: str = Field(..., description="Base64 encoded QR code image")
    secret_key: str = Field(..., description="TOTP secret key for manual entry")
    backup_codes: List[str] = Field(..., description="One-time backup codes")

class MFAVerifyRequest(BaseModel):
    mfa_code: str = Field(..., min_length=6, max_length=6, description="6-digit MFA code or backup code")

class MFAVerifyResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class MFADisableRequest(BaseModel):
    password: str = Field(..., description="Current password for verification")
    mfa_code: str = Field(..., min_length=6, max_length=6, description="Current MFA code")

class BackupCodesResponse(BaseModel):
    backup_codes: List[str] = Field(..., description="New backup codes")
    
class MFAStatus(BaseModel):
    enabled: bool
    secret_exists: bool
    backup_codes_count: int
    last_used: Optional[datetime] = None
