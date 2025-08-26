#!/usr/bin/env python3
"""
Script to create default admin user for the User Management System
Usage: python create_admin.py
"""

import sys
import os
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent.parent
sys.path.insert(0, str(app_dir))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.user import User
from app.services.auth_service import auth_service
from app.schemas.user import UserRole
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_admin_user():
    """Create default admin user"""
    
    # Admin account details as specified
    admin_email = "uynhhuc810@gmail.com"
    admin_password = "aAdDmMiInna33%$"
    admin_username = "admin"
    
    # Create database session
    db: Session = SessionLocal()
    
    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(
            User.email == admin_email
        ).first()
        
        if existing_admin:
            logger.info(f"Admin user with email {admin_email} already exists")
            return existing_admin
        
        # Check if username is taken
        existing_username = db.query(User).filter(
            User.username == admin_username
        ).first()
        
        if existing_username:
            admin_username = f"admin_{int(datetime.now().timestamp())}"
            logger.info(f"Username 'admin' taken, using '{admin_username}'")
        
        # Create admin user
        hashed_password = auth_service.get_password_hash(admin_password)
        
        admin_user = User(
            username=admin_username,
            email=admin_email,
            hashed_password=hashed_password,
            first_name="System",
            last_name="Administrator",
            role=UserRole.SUPER_ADMIN,
            is_active=True,
            is_verified=True,  # Admin is pre-verified
            mfa_enabled=False,  # Can be enabled later
            created_at=datetime.utcnow()
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        logger.info("=" * 60)
        logger.info("DEFAULT ADMIN USER CREATED SUCCESSFULLY!")
        logger.info("=" * 60)
        logger.info(f"Email: {admin_email}")
        logger.info(f"Username: {admin_username}")
        logger.info(f"Password: {admin_password}")
        logger.info(f"Role: {admin_user.role}")
        logger.info(f"User ID: {admin_user.id}")
        logger.info("=" * 60)
        logger.info("IMPORTANT: Please change the password after first login!")
        logger.info("IMPORTANT: Consider enabling MFA for this account!")
        logger.info("=" * 60)
        
        return admin_user
        
    except Exception as e:
        logger.error(f"Error creating admin user: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def create_sample_users():
    """Create some sample users for testing"""
    
    db: Session = SessionLocal()
    
    sample_users = [
        {
            "username": "john_client",
            "email": "john@example.com",
            "password": "ClientPass123!",
            "first_name": "John",
            "last_name": "Doe",
            "role": UserRole.CLIENT
        },
        {
            "username": "jane_librarian",
            "email": "jane@example.com", 
            "password": "AdminPass123!",
            "first_name": "Jane",
            "last_name": "Smith",
            "role": UserRole.ADMIN
        },
        {
            "username": "bob_reader",
            "email": "bob@example.com",
            "password": "ReaderPass123!",
            "first_name": "Bob",
            "last_name": "Johnson",
            "role": UserRole.CLIENT
        }
    ]
    
    try:
        created_users = []
        
        for user_data in sample_users:
            # Check if user exists
            existing_user = db.query(User).filter(
                User.email == user_data["email"]
            ).first()
            
            if existing_user:
                logger.info(f"User {user_data['email']} already exists, skipping")
                continue
            
            # Create user
            hashed_password = auth_service.get_password_hash(user_data["password"])
            
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=hashed_password,
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                role=user_data["role"],
                is_active=True,
                is_verified=True,  # Sample users are pre-verified
                mfa_enabled=False,
                created_at=datetime.utcnow()
            )
            
            db.add(user)
            created_users.append(user_data)
        
        if created_users:
            db.commit()
            logger.info(f"Created {len(created_users)} sample users:")
            for user_data in created_users:
                logger.info(f"  - {user_data['email']} ({user_data['role']})")
        else:
            logger.info("All sample users already exist")
            
    except Exception as e:
        logger.error(f"Error creating sample users: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main function"""
    try:
        logger.info("Creating database tables...")
        
        # Import all models to ensure tables are created
        from app.models import user, mfa, library, notification
        
        # Create all tables
        from app.models.user import Base
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database tables created successfully")
        
        # Create admin user
        logger.info("Creating default admin user...")
        admin_user = create_admin_user()
        
        # Create sample users
        create_sample = input("Create sample users for testing? (y/N): ").lower().strip()
        if create_sample in ['y', 'yes']:
            logger.info("Creating sample users...")
            create_sample_users()
        
        logger.info("Setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Setup failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
