# Multi-Factor Authentication (MFA) Implementation

## Overview

This document outlines the implementation of Multi-Factor Authentication (MFA) for the User Management Web Application, supporting both Client and Admin portals.

## MFA Flow Design

### 1. Authentication Process

1. **Primary Authentication**: Username/email + password
2. **MFA Challenge**: TOTP (Time-based One-Time Password) via authenticator app
3. **Session Establishment**: JWT token with MFA confirmation

### 2. MFA Setup Flow

1. User registers with email/password
2. Email verification required
3. User prompted to set up MFA during first login
4. QR code generated for authenticator app
5. User confirms setup with initial TOTP code
6. Backup codes generated for recovery

## Technical Implementation

### Database Schema Extensions

#### MFA Secrets Table

```sql
CREATE TABLE mfa_secrets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    secret_key VARCHAR(32) NOT NULL, -- Base32 encoded secret
    is_enabled BOOLEAN DEFAULT FALSE,
    backup_codes TEXT[], -- Array of hashed backup codes
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP WITH TIME ZONE NULL
);
```

#### Email Verification Table

```sql
CREATE TABLE email_verifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    verification_token VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    verified_at TIMESTAMP WITH TIME ZONE NULL,
    is_used BOOLEAN DEFAULT FALSE
);
```

### API Endpoints

#### MFA Setup

- `POST /api/v1/auth/mfa/setup` - Generate QR code for MFA setup
- `POST /api/v1/auth/mfa/verify-setup` - Confirm MFA setup with initial code
- `GET /api/v1/auth/mfa/backup-codes` - Generate backup codes
- `POST /api/v1/auth/mfa/disable` - Disable MFA (requires password)

#### MFA Authentication

- `POST /api/v1/auth/login` - Primary login (returns mfa_required flag)
- `POST /api/v1/auth/mfa/verify` - Verify MFA code after primary login
- `POST /api/v1/auth/mfa/backup` - Use backup code for authentication

#### Email Verification

- `POST /api/v1/auth/send-verification` - Send verification email
- `GET /api/v1/auth/verify-email/{token}` - Verify email with token

## Security Considerations

### TOTP Implementation

- **Algorithm**: HMAC-SHA1
- **Time Step**: 30 seconds
- **Code Length**: 6 digits
- **Window**: ±1 time step tolerance

### Backup Codes

- **Format**: 8 character alphanumeric
- **Count**: 10 codes per user
- **Storage**: Hashed with bcrypt
- **Single Use**: Each code can only be used once

### Rate Limiting

- **MFA Attempts**: 5 attempts per 15 minutes
- **Email Verification**: 3 emails per hour
- **Backup Code**: 3 attempts per hour

## User Experience

### Client Portal

1. Standard login with MFA prompt
2. Seamless authenticator app integration
3. Recovery options with backup codes
4. MFA management in profile settings

### Admin Portal

1. Mandatory MFA for all admin accounts
2. Enhanced security notifications
3. Ability to reset user MFA (with audit trail)
4. MFA status monitoring for all users

## Dependencies

### Backend

- `pyotp`: TOTP generation and verification
- `qrcode`: QR code generation for MFA setup
- `celery`: Background email sending
- `redis`: Task queue and rate limiting

### Frontend

- QR code display library
- TOTP input component
- Backup code management interface
