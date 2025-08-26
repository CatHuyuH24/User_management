import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from jinja2 import Environment, FileSystemLoader, Template
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from pathlib import Path
import logging
import asyncio
from datetime import datetime
from core.config import settings
from models.user import User
from models.notification import Notification
from schemas.notification import (
    NotificationType, 
    NotificationPriority, 
    NotificationStatus,
    NotificationCreate,
    EmailSendRequest
)

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for handling notifications and email sending"""
    
    def __init__(self):
        self.smtp_host = getattr(settings, 'SMTP_HOST', 'localhost')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', '')
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
        self.smtp_use_tls = getattr(settings, 'SMTP_USE_TLS', True)
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@example.com')
        self.from_name = getattr(settings, 'FROM_NAME', 'User Management System')
        
        # Initialize Jinja2 environment for email templates
        self.template_dir = Path(__file__).parent.parent / "templates" / "emails"
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.jinja_env = Environment(loader=FileSystemLoader(str(self.template_dir)))
        
        # Create default email templates if they don't exist
        self._create_default_templates()
    
    def _create_default_templates(self):
        """Create default email templates"""
        templates = {
            "welcome.html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Welcome to {{ app_name }}</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #2c3e50;">Welcome to {{ app_name }}!</h1>
        <p>Hello {{ user_name }},</p>
        <p>Welcome to our platform! Your account has been successfully created.</p>
        <div style="margin: 20px 0;">
            <strong>Account Details:</strong><br>
            Email: {{ user_email }}<br>
            Username: {{ username }}
        </div>
        <p>To get started, please verify your email address by clicking the link below:</p>
        <a href="{{ verification_link }}" style="background-color: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a>
        <p style="margin-top: 20px;">If you have any questions, feel free to contact our support team.</p>
        <p>Best regards,<br>The {{ app_name }} Team</p>
    </div>
</body>
</html>
            """,
            "email_verification.html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Verify Your Email</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #2c3e50;">Email Verification</h1>
        <p>Hello {{ user_name }},</p>
        <p>Please verify your email address by clicking the link below:</p>
        <a href="{{ verification_link }}" style="background-color: #27ae60; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email</a>
        <p style="margin-top: 20px;">This link will expire in 24 hours.</p>
        <p>If you didn't create an account, please ignore this email.</p>
        <p>Best regards,<br>The {{ app_name }} Team</p>
    </div>
</body>
</html>
            """,
            "password_reset.html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Password Reset</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #e74c3c;">Password Reset Request</h1>
        <p>Hello {{ user_name }},</p>
        <p>You requested a password reset for your account. Click the link below to reset your password:</p>
        <a href="{{ reset_link }}" style="background-color: #e74c3c; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a>
        <p style="margin-top: 20px;">This link will expire in 1 hour.</p>
        <p>If you didn't request this, please ignore this email and your password will remain unchanged.</p>
        <p>Best regards,<br>The {{ app_name }} Team</p>
    </div>
</body>
</html>
            """,
            "book_due_reminder.html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Book Due Reminder</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #f39c12;">Book Due Reminder</h1>
        <p>Hello {{ user_name }},</p>
        <p>This is a reminder that the following book is due soon:</p>
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <strong>{{ book_title }}</strong> by {{ book_author }}<br>
            Due Date: {{ due_date }}<br>
            Days remaining: {{ days_remaining }}
        </div>
        <p>Please return the book by the due date to avoid late fees.</p>
        <p>Best regards,<br>The {{ app_name }} Library Team</p>
    </div>
</body>
</html>
            """,
            "book_overdue.html": """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Overdue Book Notice</title>
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1 style="color: #e74c3c;">Overdue Book Notice</h1>
        <p>Hello {{ user_name }},</p>
        <p>The following book is overdue and should be returned immediately:</p>
        <div style="background-color: #ffebee; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #e74c3c;">
            <strong>{{ book_title }}</strong> by {{ book_author }}<br>
            Due Date: {{ due_date }}<br>
            Days overdue: {{ days_overdue }}<br>
            Fine amount: ${{ fine_amount }}
        </div>
        <p>Please return the book as soon as possible to avoid additional fees.</p>
        <p>Best regards,<br>The {{ app_name }} Library Team</p>
    </div>
</body>
</html>
            """
        }
        
        for filename, content in templates.items():
            template_path = self.template_dir / filename
            if not template_path.exists():
                template_path.write_text(content.strip())
    
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: Optional[str] = None,
        text_content: Optional[str] = None,
        template_name: Optional[str] = None,
        template_variables: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Use template if provided
            if template_name and template_variables:
                try:
                    template = self.jinja_env.get_template(template_name)
                    html_content = template.render(**template_variables)
                except Exception as e:
                    logger.error(f"Error rendering template {template_name}: {str(e)}")
                    # Fall back to plain content
            
            # Add text content
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML content
            if html_content:
                html_part = MIMEText(html_content, 'html')
                msg.attach(html_part)
            
            # Send email
            if self.smtp_use_tls:
                await aiosmtplib.send(
                    msg,
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    start_tls=True,
                    username=self.smtp_username,
                    password=self.smtp_password
                )
            else:
                await aiosmtplib.send(
                    msg,
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    username=self.smtp_username,
                    password=self.smtp_password
                )
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False
    
    def create_notification(
        self, 
        db: Session, 
        user_id: int, 
        notification_type: NotificationType,
        title: str,
        message: str,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        send_email: bool = True,
        email_template: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Notification:
        """Create a new notification"""
        try:
            notification = Notification(
                user_id=user_id,
                type=notification_type,
                title=title,
                message=message,
                priority=priority,
                status=NotificationStatus.PENDING,
                metadata=metadata
            )
            
            db.add(notification)
            db.commit()
            db.refresh(notification)
            
            # Send email if requested
            if send_email:
                user = db.query(User).filter(User.id == user_id).first()
                if user and user.email:
                    # Schedule email sending (in production, use Celery)
                    asyncio.create_task(self._send_notification_email(
                        notification, user, email_template
                    ))
            
            return notification
            
        except Exception as e:
            logger.error(f"Error creating notification: {str(e)}")
            db.rollback()
            raise
    
    async def _send_notification_email(
        self, 
        notification: Notification, 
        user: User, 
        template_name: Optional[str] = None
    ):
        """Send email for notification"""
        try:
            # Prepare template variables
            template_variables = {
                'user_name': f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username,
                'user_email': user.email,
                'username': user.username,
                'app_name': getattr(settings, 'APP_NAME', 'User Management System'),
                'notification_title': notification.title,
                'notification_message': notification.message,
                'notification_type': notification.type.value,
            }
            
            # Add metadata if available
            if notification.metadata:
                template_variables.update(notification.metadata)
            
            # Determine template based on notification type if not provided
            if not template_name:
                template_map = {
                    NotificationType.EMAIL_VERIFICATION: "email_verification.html",
                    NotificationType.PASSWORD_RESET: "password_reset.html",
                    NotificationType.ACCOUNT_CREATED: "welcome.html",
                    NotificationType.BOOK_DUE_SOON: "book_due_reminder.html",
                    NotificationType.BOOK_OVERDUE: "book_overdue.html",
                }
                template_name = template_map.get(notification.type)
            
            # Send email
            success = await self.send_email(
                to_email=user.email,
                subject=notification.title,
                template_name=template_name,
                template_variables=template_variables,
                text_content=notification.message  # Fallback
            )
            
            # Update notification status
            if success:
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.utcnow()
            else:
                notification.status = NotificationStatus.FAILED
            
        except Exception as e:
            logger.error(f"Error sending notification email: {str(e)}")
            notification.status = NotificationStatus.FAILED
    
    def send_welcome_email(self, db: Session, user: User, verification_link: str = None):
        """Send welcome email to new user"""
        metadata = {
            'verification_link': verification_link or '#'
        }
        
        return self.create_notification(
            db=db,
            user_id=user.id,
            notification_type=NotificationType.ACCOUNT_CREATED,
            title=f"Welcome to {getattr(settings, 'APP_NAME', 'User Management System')}!",
            message=f"Welcome {user.username}! Your account has been created successfully.",
            priority=NotificationPriority.NORMAL,
            send_email=True,
            email_template="welcome.html",
            metadata=metadata
        )
    
    def send_email_verification(self, db: Session, user: User, verification_link: str):
        """Send email verification"""
        metadata = {
            'verification_link': verification_link
        }
        
        return self.create_notification(
            db=db,
            user_id=user.id,
            notification_type=NotificationType.EMAIL_VERIFICATION,
            title="Please verify your email address",
            message="Click the link in this email to verify your account.",
            priority=NotificationPriority.HIGH,
            send_email=True,
            email_template="email_verification.html",
            metadata=metadata
        )
    
    def send_password_reset(self, db: Session, user: User, reset_link: str):
        """Send password reset email"""
        metadata = {
            'reset_link': reset_link
        }
        
        return self.create_notification(
            db=db,
            user_id=user.id,
            notification_type=NotificationType.PASSWORD_RESET,
            title="Password Reset Request",
            message="Click the link to reset your password.",
            priority=NotificationPriority.HIGH,
            send_email=True,
            email_template="password_reset.html",
            metadata=metadata
        )
    
    def send_book_due_reminder(
        self, 
        db: Session, 
        user: User, 
        book_title: str, 
        book_author: str, 
        due_date: str, 
        days_remaining: int
    ):
        """Send book due reminder"""
        metadata = {
            'book_title': book_title,
            'book_author': book_author,
            'due_date': due_date,
            'days_remaining': days_remaining
        }
        
        return self.create_notification(
            db=db,
            user_id=user.id,
            notification_type=NotificationType.BOOK_DUE_SOON,
            title=f"Book Due Soon: {book_title}",
            message=f"Your book '{book_title}' is due in {days_remaining} days.",
            priority=NotificationPriority.NORMAL,
            send_email=True,
            email_template="book_due_reminder.html",
            metadata=metadata
        )
    
    def send_book_overdue_notice(
        self, 
        db: Session, 
        user: User, 
        book_title: str, 
        book_author: str, 
        due_date: str, 
        days_overdue: int,
        fine_amount: float
    ):
        """Send book overdue notice"""
        metadata = {
            'book_title': book_title,
            'book_author': book_author,
            'due_date': due_date,
            'days_overdue': days_overdue,
            'fine_amount': f"{fine_amount:.2f}"
        }
        
        return self.create_notification(
            db=db,
            user_id=user.id,
            notification_type=NotificationType.BOOK_OVERDUE,
            title=f"Overdue Book: {book_title}",
            message=f"Your book '{book_title}' is {days_overdue} days overdue. Fine: ${fine_amount:.2f}",
            priority=NotificationPriority.HIGH,
            send_email=True,
            email_template="book_overdue.html",
            metadata=metadata
        )
    
    def mark_notification_as_read(self, db: Session, notification_id: int, user_id: int) -> bool:
        """Mark notification as read"""
        try:
            notification = db.query(Notification).filter(
                Notification.id == notification_id,
                Notification.user_id == user_id
            ).first()
            
            if notification:
                notification.status = NotificationStatus.READ
                notification.read_at = datetime.utcnow()
                db.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            db.rollback()
            return False
    
    def get_user_notifications(
        self, 
        db: Session, 
        user_id: int, 
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """Get notifications for a user"""
        try:
            query = db.query(Notification).filter(Notification.user_id == user_id)
            
            if unread_only:
                query = query.filter(Notification.status != NotificationStatus.READ)
            
            return query.order_by(Notification.created_at.desc()).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {str(e)}")
            return []

# Create singleton instance
notification_service = NotificationService()
