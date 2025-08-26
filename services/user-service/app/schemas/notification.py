from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    LOGIN_ALERT = "login_alert"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    ACCOUNT_CREATED = "account_created"
    ACCOUNT_DELETED = "account_deleted"
    BOOK_BORROWED = "book_borrowed"
    BOOK_DUE_SOON = "book_due_soon"
    BOOK_OVERDUE = "book_overdue"
    BOOK_RETURNED = "book_returned"
    FINE_APPLIED = "fine_applied"
    ADMIN_MESSAGE = "admin_message"
    SYSTEM_MAINTENANCE = "system_maintenance"

class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    READ = "read"

# Notification schemas
class NotificationCreate(BaseModel):
    user_id: int
    type: NotificationType
    title: str = Field(..., max_length=200)
    message: str = Field(..., max_length=2000)
    priority: NotificationPriority = NotificationPriority.NORMAL
    send_email: bool = True
    email_template: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority
    status: NotificationStatus
    sent_at: Optional[datetime]
    read_at: Optional[datetime]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationUpdate(BaseModel):
    status: Optional[NotificationStatus] = None
    read_at: Optional[datetime] = None

class NotificationFilters(BaseModel):
    user_id: Optional[int] = None
    type: Optional[NotificationType] = None
    status: Optional[NotificationStatus] = None
    priority: Optional[NotificationPriority] = None
    unread_only: bool = False
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

# Email schemas
class EmailTemplate(BaseModel):
    name: str = Field(..., max_length=100)
    subject: str = Field(..., max_length=200)
    html_content: str
    text_content: Optional[str] = None
    variables: Optional[Dict[str, str]] = None

class EmailSendRequest(BaseModel):
    to_email: EmailStr
    subject: str = Field(..., max_length=200)
    html_content: Optional[str] = None
    text_content: Optional[str] = None
    template_name: Optional[str] = None
    template_variables: Optional[Dict[str, Any]] = None
    priority: NotificationPriority = NotificationPriority.NORMAL

class EmailSendResponse(BaseModel):
    message: str
    email_id: Optional[str] = None
    status: str

# Bulk notification schemas
class BulkNotificationCreate(BaseModel):
    user_ids: List[int] = Field(..., min_items=1, max_items=1000)
    type: NotificationType
    title: str = Field(..., max_length=200)
    message: str = Field(..., max_length=2000)
    priority: NotificationPriority = NotificationPriority.NORMAL
    send_email: bool = True
    email_template: Optional[str] = None

class NotificationStats(BaseModel):
    total_notifications: int
    pending_notifications: int
    sent_notifications: int
    failed_notifications: int
    unread_notifications: int
    notifications_by_type: Dict[str, int]
    notifications_by_priority: Dict[str, int]
