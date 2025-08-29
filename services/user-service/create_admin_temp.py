#!/usr/bin/env python3
"""
Script to create admin users directly in the database
"""
import sys
import os
sys.path.append('/app')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import SQLALCHEMY_DATABASE_URL
from models.user import User, UserRole
from core.security import get_password_hash

def create_admin_user():
    """Create an admin user in the database"""
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == "admin@example.com").first()
        if existing_admin:
            existing_admin.role = UserRole.ADMIN
            db.commit()
            print(f"Updated existing user {existing_admin.username} to admin role")
        else:
            # Create new admin user
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("AdminPassword123!"),
                first_name="Admin",
                last_name="User",
                is_active=True,
                is_verified=True,
                role=UserRole.ADMIN
            )
            
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"Created admin user: {admin_user.username} (ID: {admin_user.id})")
        
        # Also create a super admin
        existing_super_admin = db.query(User).filter(User.email == "superadmin@example.com").first()
        if not existing_super_admin:
            super_admin_user = User(
                username="superadmin",
                email="superadmin@example.com",
                hashed_password=get_password_hash("SuperAdminPassword123!"),
                first_name="Super",
                last_name="Admin",
                is_active=True,
                is_verified=True,
                role=UserRole.SUPER_ADMIN
            )
            
            db.add(super_admin_user)
            db.commit()
            db.refresh(super_admin_user)
            print(f"Created super admin user: {super_admin_user.username} (ID: {super_admin_user.id})")
    
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
