from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from .user import UserRole, UserResponse

class AdminAction(str, Enum):
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_ACTIVATED = "user_activated"
    USER_DEACTIVATED = "user_deactivated"
    ROLE_CHANGED = "role_changed"
    PASSWORD_RESET = "password_reset"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    BOOK_CREATED = "book_created"
    BOOK_UPDATED = "book_updated"
    BOOK_DELETED = "book_deleted"
    LOAN_CREATED = "loan_created"
    LOAN_UPDATED = "loan_updated"
    FINE_APPLIED = "fine_applied"
    FINE_WAIVED = "fine_waived"

# Admin user management schemas
class AdminUserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    role: UserRole = Field(UserRole.CLIENT, description="User role")
    is_active: bool = True
    is_verified: bool = False
    send_welcome_email: bool = True

class AdminUserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    year_of_birth: Optional[int] = Field(None, ge=1900, le=2024)
    description: Optional[str] = Field(None, max_length=1000)

class AdminUserResponse(UserResponse):
    last_login: Optional[datetime]
    login_count: int
    mfa_enabled: bool
    created_by_admin: Optional[str]
    last_modified_by: Optional[str]
    last_modified_at: Optional[datetime]

class UserDeletionRequest(BaseModel):
    reason: str = Field(..., min_length=10, max_length=500, description="Reason for deletion")
    permanent: bool = Field(False, description="Permanent deletion (cannot be recovered)")
    notify_user: bool = Field(True, description="Send deletion notification to user")

class UserDeletionResponse(BaseModel):
    message: str
    user_id: int
    deleted_at: datetime
    deleted_by: str
    reason: str
    permanent: bool
    recoverable_until: Optional[datetime]

# Password reset schemas
class AdminPasswordReset(BaseModel):
    user_id: int
    new_password: str = Field(..., min_length=8)
    force_password_change: bool = Field(True, description="Force user to change password on next login")
    notify_user: bool = Field(True, description="Send password reset notification to user")

# Bulk operations
class BulkUserUpdate(BaseModel):
    user_ids: List[int] = Field(..., min_items=1, max_items=100)
    updates: AdminUserUpdate
    notify_users: bool = Field(False, description="Send update notification to affected users")

class BulkUserAction(BaseModel):
    user_ids: List[int] = Field(..., min_items=1, max_items=100)
    action: str = Field(..., description="Action to perform: activate, deactivate, verify, unverify")
    reason: Optional[str] = Field(None, max_length=500)
    notify_users: bool = Field(True, description="Send notification to affected users")

# Audit log schemas
class AuditLogEntry(BaseModel):
    id: int
    admin_user_id: int
    admin_username: str
    target_user_id: Optional[int]
    target_username: Optional[str]
    action: AdminAction
    details: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True

class AuditLogFilters(BaseModel):
    admin_user_id: Optional[int] = None
    target_user_id: Optional[int] = None
    action: Optional[AdminAction] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    search: Optional[str] = Field(None, description="Search in details, usernames")

# Admin dashboard statistics
class AdminDashboardStats(BaseModel):
    total_users: int
    active_users: int
    verified_users: int
    users_with_mfa: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int
    total_books: int
    total_loans: int
    active_loans: int
    overdue_loans: int
    total_fines: float
    pending_verifications: int
    recent_activity: List[AuditLogEntry]

# System settings
class SystemSettings(BaseModel):
    site_name: str = Field(..., max_length=100)
    admin_email: EmailStr
    max_login_attempts: int = Field(5, ge=1, le=20)
    session_timeout_minutes: int = Field(30, ge=5, le=480)
    password_expiry_days: Optional[int] = Field(None, ge=30, le=365)
    require_email_verification: bool = True
    allow_self_registration: bool = True
    default_user_role: UserRole = UserRole.CLIENT
    max_book_loans_per_user: int = Field(5, ge=1, le=50)
    loan_duration_days: int = Field(14, ge=1, le=365)
    fine_per_day: float = Field(0.50, ge=0, le=100)
    enable_notifications: bool = True
    enable_email_reminders: bool = True
