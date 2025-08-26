from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional
from datetime import datetime
from core.database import get_db
from services.auth_service import auth_service, get_current_active_user_dependency, require_admin_dependency
from services.notification_service import notification_service
from models.user import User
from models.notification import Notification
from schemas.notification import (
    NotificationResponse,
    NotificationCreate,
    NotificationUpdate,
    NotificationFilters,
    NotificationStats,
    EmailSendRequest,
    EmailSendResponse,
    BulkNotificationCreate,
    NotificationType,
    NotificationPriority,
    NotificationStatus
)
from schemas.user import UserRole
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    unread_only: bool = Query(False),
    type_filter: Optional[NotificationType] = Query(None),
    priority_filter: Optional[NotificationPriority] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """Get notifications for current user"""
    try:
        query = db.query(Notification).filter(Notification.user_id == current_user.id)
        
        # Apply filters
        if unread_only:
            query = query.filter(Notification.status != NotificationStatus.READ)
        
        if type_filter:
            query = query.filter(Notification.type == type_filter)
        
        if priority_filter:
            query = query.filter(Notification.priority == priority_filter)
        
        # Get notifications with pagination
        notifications = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()
        
        return [NotificationResponse.model_validate(notif) for notif in notifications]
        
    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get notifications"
        )

@router.get("/unread-count")
async def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """Get count of unread notifications"""
    try:
        count = db.query(Notification).filter(
            and_(
                Notification.user_id == current_user.id,
                Notification.status != NotificationStatus.READ
            )
        ).count()
        
        return {"unread_count": count}
        
    except Exception as e:
        logger.error(f"Error getting unread count: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get unread count"
        )

@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """Mark notification as read"""
    try:
        success = notification_service.mark_notification_as_read(
            db, notification_id, current_user.id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        return {"message": "Notification marked as read"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark notification as read"
        )

@router.put("/mark-all-read")
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """Mark all notifications as read for current user"""
    try:
        updated_count = db.query(Notification).filter(
            and_(
                Notification.user_id == current_user.id,
                Notification.status != NotificationStatus.READ
            )
        ).update({
            Notification.status: NotificationStatus.READ,
            Notification.read_at: datetime.utcnow()
        })
        
        db.commit()
        
        return {
            "message": f"Marked {updated_count} notifications as read",
            "updated_count": updated_count
        }
        
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to mark all notifications as read"
        )

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """Delete notification"""
    try:
        notification = db.query(Notification).filter(
            and_(
                Notification.id == notification_id,
                Notification.user_id == current_user.id
            )
        ).first()
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found"
            )
        
        db.delete(notification)
        db.commit()
        
        return {"message": "Notification deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting notification: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete notification"
        )

# Admin endpoints
@router.post("/admin/send", status_code=status.HTTP_201_CREATED)
async def create_notification_admin(
    notification_create: NotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_dependency)
):
    """Create notification as admin"""
    try:
        # Verify target user exists
        target_user = db.query(User).filter(User.id == notification_create.user_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target user not found"
            )
        
        notification = notification_service.create_notification(
            db=db,
            user_id=notification_create.user_id,
            notification_type=notification_create.type,
            title=notification_create.title,
            message=notification_create.message,
            priority=notification_create.priority,
            send_email=notification_create.send_email,
            email_template=notification_create.email_template,
            metadata=notification_create.metadata
        )
        
        logger.info(f"Notification created by admin {current_user.id} for user {notification_create.user_id}")
        
        return NotificationResponse.model_validate(notification)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create notification"
        )

@router.post("/admin/bulk-send", status_code=status.HTTP_201_CREATED)
async def create_bulk_notifications(
    bulk_notification: BulkNotificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_dependency)
):
    """Create bulk notifications as admin"""
    try:
        # Verify all target users exist
        users = db.query(User).filter(User.id.in_(bulk_notification.user_ids)).all()
        found_user_ids = {user.id for user in users}
        missing_user_ids = set(bulk_notification.user_ids) - found_user_ids
        
        if missing_user_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Users not found: {list(missing_user_ids)}"
            )
        
        created_notifications = []
        
        for user_id in bulk_notification.user_ids:
            try:
                notification = notification_service.create_notification(
                    db=db,
                    user_id=user_id,
                    notification_type=bulk_notification.type,
                    title=bulk_notification.title,
                    message=bulk_notification.message,
                    priority=bulk_notification.priority,
                    send_email=bulk_notification.send_email,
                    email_template=bulk_notification.email_template,
                    metadata=None
                )
                created_notifications.append(notification)
                
            except Exception as e:
                logger.error(f"Error creating notification for user {user_id}: {str(e)}")
                continue
        
        logger.info(f"Bulk notifications created by admin {current_user.id} for {len(created_notifications)} users")
        
        return {
            "message": f"Successfully created {len(created_notifications)} notifications",
            "created_count": len(created_notifications),
            "total_requested": len(bulk_notification.user_ids)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating bulk notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create bulk notifications"
        )

@router.get("/admin/all", response_model=List[NotificationResponse])
async def get_all_notifications_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    user_id: Optional[int] = Query(None),
    type_filter: Optional[NotificationType] = Query(None),
    status_filter: Optional[NotificationStatus] = Query(None),
    priority_filter: Optional[NotificationPriority] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_dependency)
):
    """Get all notifications (Admin only)"""
    try:
        query = db.query(Notification)
        
        # Apply filters
        if user_id:
            query = query.filter(Notification.user_id == user_id)
        
        if type_filter:
            query = query.filter(Notification.type == type_filter)
        
        if status_filter:
            query = query.filter(Notification.status == status_filter)
        
        if priority_filter:
            query = query.filter(Notification.priority == priority_filter)
        
        # Get notifications with pagination
        notifications = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()
        
        return [NotificationResponse.model_validate(notif) for notif in notifications]
        
    except Exception as e:
        logger.error(f"Error getting all notifications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get all notifications"
        )

@router.get("/admin/stats", response_model=NotificationStats)
async def get_notification_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_dependency)
):
    """Get notification statistics (Admin only)"""
    try:
        total_notifications = db.query(Notification).count()
        pending_notifications = db.query(Notification).filter(
            Notification.status == NotificationStatus.PENDING
        ).count()
        sent_notifications = db.query(Notification).filter(
            Notification.status == NotificationStatus.SENT
        ).count()
        failed_notifications = db.query(Notification).filter(
            Notification.status == NotificationStatus.FAILED
        ).count()
        unread_notifications = db.query(Notification).filter(
            Notification.status != NotificationStatus.READ
        ).count()
        
        # Get notifications by type
        notifications_by_type = {}
        type_counts = db.query(
            Notification.type, 
            db.func.count(Notification.id)
        ).group_by(Notification.type).all()
        
        for notification_type, count in type_counts:
            notifications_by_type[notification_type.value] = count
        
        # Get notifications by priority
        notifications_by_priority = {}
        priority_counts = db.query(
            Notification.priority, 
            db.func.count(Notification.id)
        ).group_by(Notification.priority).all()
        
        for priority, count in priority_counts:
            notifications_by_priority[priority.value] = count
        
        return NotificationStats(
            total_notifications=total_notifications,
            pending_notifications=pending_notifications,
            sent_notifications=sent_notifications,
            failed_notifications=failed_notifications,
            unread_notifications=unread_notifications,
            notifications_by_type=notifications_by_type,
            notifications_by_priority=notifications_by_priority
        )
        
    except Exception as e:
        logger.error(f"Error getting notification stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get notification statistics"
        )

@router.post("/admin/send-email", response_model=EmailSendResponse)
async def send_email_admin(
    email_request: EmailSendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_dependency)
):
    """Send email directly (Admin only)"""
    try:
        success = await notification_service.send_email(
            to_email=email_request.to_email,
            subject=email_request.subject,
            html_content=email_request.html_content,
            text_content=email_request.text_content,
            template_name=email_request.template_name,
            template_variables=email_request.template_variables
        )
        
        if success:
            logger.info(f"Email sent by admin {current_user.id} to {email_request.to_email}")
            return EmailSendResponse(
                message="Email sent successfully",
                status="sent"
            )
        else:
            return EmailSendResponse(
                message="Failed to send email",
                status="failed"
            )
        
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email"
        )
