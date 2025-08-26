from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import Optional

from models.user import User
from schemas.user import UserCreate, UserUpdate
from core.security import get_password_hash, verify_password
from datetime import datetime

class UserService:
    """Service layer for user operations."""
    
    def create_user(self, db: Session, user_create: UserCreate) -> User:
        """Create a new user."""
        try:
            # Check if user already exists
            if self.get_user_by_email(db, user_create.email):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            if self.get_user_by_username(db, user_create.username):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            
            # Create user with hashed password
            hashed_password = get_password_hash(user_create.password)
            
            db_user = User(
                username=user_create.username,
                email=user_create.email,
                hashed_password=hashed_password,
                first_name=user_create.first_name,
                last_name=user_create.last_name,
                is_active=True,
                is_verified=True  # Users are verified by default (no email verification required)
            )
            
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
            
        except IntegrityError as e:
            db.rollback()
            if "users_email_key" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            elif "users_username_key" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user"
                )
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()
    
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()
    
    def get_user_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()
    
    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password."""
        user = self.get_user_by_email(db, email)
        if not user:
            return None
        if not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        return user
    
    def update_user(self, db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update user profile."""
        user = self.get_user_by_id(db, user_id)
        if not user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user
    
    def deactivate_user(self, db: Session, user_id: int) -> bool:
        """Deactivate user account."""
        user = self.get_user_by_id(db, user_id)
        if not user:
            return False
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.commit()
        return True

# Create service instance
user_service = UserService()
