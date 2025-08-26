from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional
from datetime import datetime, date
from core.database import get_db
from services.auth_service import auth_service, get_current_active_user_dependency, require_admin_dependency
from services.user_service import user_service
from models.user import User
from schemas.admin import (
    AdminUserCreate,
    AdminUserUpdate,
    AdminUserResponse,
    UserDeletionRequest,
    UserDeletionResponse,
    AdminPasswordReset,
    BulkUserUpdate,
    BulkUserAction,
    AuditLogEntry,
    AuditLogFilters,
    AdminDashboardStats,
    SystemSettings
)
from schemas.user import UserRole
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/dashboard", response_model=AdminDashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_dependency)
):
    """Get admin dashboard statistics"""
    try:
        # User statistics
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        verified_users = db.query(User).filter(User.is_verified == True).count()
        users_with_mfa = db.query(User).filter(User.mfa_enabled == True).count()
        
        # New users statistics
        today = date.today()
        new_users_today = db.query(User).filter(
            func.date(User.created_at) == today
        ).count()
        
        # This would require actual library models when implemented
        total_books = 0
        total_loans = 0
        active_loans = 0
        overdue_loans = 0
        total_fines = 0.0
        
        pending_verifications = db.query(User).filter(
            and_(User.is_active == True, User.is_verified == False)
        ).count()
        
        # Recent activity (placeholder - would need audit log table)
        recent_activity = []
        
        return AdminDashboardStats(
            total_users=total_users,
            active_users=active_users,
            verified_users=verified_users,
            users_with_mfa=users_with_mfa,
            new_users_today=new_users_today,
            new_users_this_week=0,  # Would need proper date calculations
            new_users_this_month=0,
            total_books=total_books,
            total_loans=total_loans,
            active_loans=active_loans,
            overdue_loans=overdue_loans,
            total_fines=total_fines,
            pending_verifications=pending_verifications,
            recent_activity=recent_activity
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard statistics"
        )

@router.get("/users", response_model=List[AdminUserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
    role: Optional[UserRole] = Query(None),
    is_active: Optional[bool] = Query(None),
    is_verified: Optional[bool] = Query(None),
    mfa_enabled: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_dependency)
):
    """Get all users with filtering and pagination"""
    try:
        query = db.query(User)
        
        # Apply filters
        if search:
            search_filter = or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        if role is not None:
            query = query.filter(User.role == role)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        if is_verified is not None:
            query = query.filter(User.is_verified == is_verified)
        
        if mfa_enabled is not None:
            query = query.filter(User.mfa_enabled == mfa_enabled)
        
        # Get users with pagination
        users = query.order_by(desc(User.created_at)).offset(skip).limit(limit).all()
        
        # Convert to AdminUserResponse
        admin_users = []
        for user in users:
            admin_user = AdminUserResponse(
                **user.__dict__,
                login_count=0,  # Field doesn't exist in User model yet
                created_by_admin=None,  # Would need audit trail
                last_modified_by=None,
                last_modified_at=None
            )
            admin_users.append(admin_user)
        
        return admin_users
        
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users"
        )

@router.post("/users", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_as_admin(
    user_create: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_dependency)
):
    """Create a new user as admin"""
    try:
        # Convert AdminUserCreate to UserCreate
        from schemas.user import UserCreate
        user_data = UserCreate(
            username=user_create.username,
            email=user_create.email,
            password=user_create.password,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            role=user_create.role
        )
        
        # Create user
        user = user_service.create_user(db, user_data)
        
        # Set admin-specific fields
        user.is_active = user_create.is_active
        user.is_verified = user_create.is_verified
        
        db.commit()
        
        # Send welcome email if requested
        if user_create.send_welcome_email:
            # TODO: Implement email service
            logger.info(f"Welcome email should be sent to {user.email}")
        
        # Log admin action
        logger.info(f"User {user.id} created by admin {current_user.id}")
        
        return AdminUserResponse(
            **user.__dict__,
            last_login=None,
            login_count=0,
            created_by_admin=current_user.username,
            last_modified_by=current_user.username,
            last_modified_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user as admin: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_dependency)
):
    """Get user by ID"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return AdminUserResponse(
            **user.__dict__,
            last_login=getattr(user, 'last_login', None),
            login_count=getattr(user, 'login_count', 0),
            created_by_admin=None,
            last_modified_by=None,
            last_modified_at=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user by ID: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user"
        )

@router.put("/users/{user_id}", response_model=AdminUserResponse)
async def update_user(
    user_id: int,
    user_update: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_dependency)
):
    """Update user as admin"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update fields
        update_data = user_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        db.commit()
        
        # Log admin action
        logger.info(f"User {user_id} updated by admin {current_user.id}")
        
        return AdminUserResponse(
            **user.__dict__,
            last_login=getattr(user, 'last_login', None),
            login_count=getattr(user, 'login_count', 0),
            created_by_admin=None,
            last_modified_by=current_user.username,
            last_modified_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )

@router.delete("/users/{user_id}", response_model=UserDeletionResponse)
async def delete_user(
    user_id: int,
    deletion_request: UserDeletionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_dependency)
):
    """Delete user (soft delete by default, permanent if specified)"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Prevent self-deletion
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete your own account"
            )
        
        # Prevent deletion of super admin by regular admin
        if (user.role == UserRole.SUPER_ADMIN and 
            current_user.role != UserRole.SUPER_ADMIN):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete super admin account"
            )
        
        deleted_at = datetime.utcnow()
        
        if deletion_request.permanent:
            # Permanent deletion
            db.delete(user)
            recoverable_until = None
        else:
            # Soft deletion
            user.is_active = False
            user.deleted_at = deleted_at
            # Set recovery period (e.g., 30 days)
            from datetime import timedelta
            recoverable_until = deleted_at + timedelta(days=30)
        
        db.commit()
        
        # Send notification if requested
        if deletion_request.notify_user:
            # TODO: Implement email notification
            logger.info(f"Deletion notification should be sent to {user.email}")
        
        # Log admin action
        logger.info(f"User {user_id} deleted by admin {current_user.id}")
        
        return UserDeletionResponse(
            message="User deleted successfully",
            user_id=user_id,
            deleted_at=deleted_at,
            deleted_by=current_user.username,
            reason=deletion_request.reason,
            permanent=deletion_request.permanent,
            recoverable_until=recoverable_until
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

@router.post("/users/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    password_reset: AdminPasswordReset,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_dependency)
):
    """Reset user password as admin"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Hash new password
        hashed_password = auth_service.get_password_hash(password_reset.new_password)
        user.hashed_password = hashed_password
        
        # Set password change requirement if requested
        if password_reset.force_password_change:
            user.password_reset_required = True
        
        user.updated_at = datetime.utcnow()
        db.commit()
        
        # Send notification if requested
        if password_reset.notify_user:
            # TODO: Implement email notification
            logger.info(f"Password reset notification should be sent to {user.email}")
        
        # Log admin action
        logger.info(f"Password reset for user {user_id} by admin {current_user.id}")
        
        return {"message": "Password reset successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resetting password: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )

@router.post("/users/bulk-update")
async def bulk_update_users(
    bulk_update: BulkUserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_dependency)
):
    """Bulk update multiple users"""
    try:
        # Get users to update
        users = db.query(User).filter(User.id.in_(bulk_update.user_ids)).all()
        
        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No users found with provided IDs"
            )
        
        # Update fields
        update_data = bulk_update.updates.model_dump(exclude_unset=True)
        updated_count = 0
        
        for user in users:
            for field, value in update_data.items():
                if hasattr(user, field):
                    setattr(user, field, value)
            user.updated_at = datetime.utcnow()
            updated_count += 1
        
        db.commit()
        
        # Send notifications if requested
        if bulk_update.notify_users:
            # TODO: Implement bulk email notifications
            logger.info(f"Bulk update notifications should be sent to {updated_count} users")
        
        # Log admin action
        logger.info(f"Bulk update of {updated_count} users by admin {current_user.id}")
        
        return {
            "message": f"Successfully updated {updated_count} users",
            "updated_count": updated_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk update: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to bulk update users"
        )

@router.post("/users/bulk-action")
async def bulk_user_action(
    bulk_action: BulkUserAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_dependency)
):
    """Perform bulk actions on multiple users"""
    try:
        # Get users
        users = db.query(User).filter(User.id.in_(bulk_action.user_ids)).all()
        
        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No users found with provided IDs"
            )
        
        action_count = 0
        
        for user in users:
            if bulk_action.action == "activate":
                user.is_active = True
                action_count += 1
            elif bulk_action.action == "deactivate":
                user.is_active = False
                action_count += 1
            elif bulk_action.action == "verify":
                user.is_verified = True
                action_count += 1
            elif bulk_action.action == "unverify":
                user.is_verified = False
                action_count += 1
            
            user.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Send notifications if requested
        if bulk_action.notify_users:
            # TODO: Implement bulk email notifications
            logger.info(f"Bulk action notifications should be sent to {action_count} users")
        
        # Log admin action
        logger.info(f"Bulk action '{bulk_action.action}' on {action_count} users by admin {current_user.id}")
        
        return {
            "message": f"Successfully performed '{bulk_action.action}' on {action_count} users",
            "action": bulk_action.action,
            "affected_count": action_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk action: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform bulk action"
        )
