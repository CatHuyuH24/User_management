#!/usr/bin/env python3
"""
Script to create the default admin account.
This script is designed to run inside the Docker container.
"""

import asyncio
import sys
from sqlalchemy.orm import Session
from core.database import SessionLocal, engine, Base
from models.user import User, UserRole
from services.auth_service import auth_service
from services.user_service import user_service
from schemas.user import UserCreate

# Default admin account details
DEFAULT_ADMIN_EMAIL = "uynhhuc810@gmail.com"
DEFAULT_ADMIN_PASSWORD = "aAdDmMiInna33%$"
DEFAULT_ADMIN_USERNAME = "super_admin"

def create_default_admin():
    """Create the default admin account if it doesn't exist."""
    
    print("🚀 Setting up default admin account...")
    
    # Create all database tables
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created/verified")
    except Exception as e:
        print(f"❌ Error creating database tables: {str(e)}")
        return False
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(
            User.email == DEFAULT_ADMIN_EMAIL
        ).first()
        
        if existing_admin:
            print(f"✅ Admin account already exists: {DEFAULT_ADMIN_EMAIL}")
            print(f"   Username: {existing_admin.username}")
            print(f"   Role: {existing_admin.role.value}")
            print(f"   Active: {existing_admin.is_active}")
            print(f"   Verified: {existing_admin.is_verified}")
            return True
        
        # Create admin user
        admin_data = UserCreate(
            username=DEFAULT_ADMIN_USERNAME,
            email=DEFAULT_ADMIN_EMAIL,
            password=DEFAULT_ADMIN_PASSWORD,
            first_name="Super",
            last_name="Admin"
        )
        
        # Use user service to create admin
        admin_user = user_service.create_user(db, admin_data)
        
        # Set role to super admin
        admin_user.role = UserRole.SUPER_ADMIN
        admin_user.is_verified = True
        admin_user.is_active = True
        
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Default admin account created successfully!")
        print(f"   Email: {DEFAULT_ADMIN_EMAIL}")
        print(f"   Username: {DEFAULT_ADMIN_USERNAME}")
        print(f"   Password: {DEFAULT_ADMIN_PASSWORD}")
        print(f"   Role: {admin_user.role.value}")
        print("")
        print("⚠️  IMPORTANT: Change the default password after first login!")
        print("⚠️  This admin account has full system access.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating default admin account: {str(e)}")
        db.rollback()
        return False
        
    finally:
        db.close()

def main():
    """Main function to create admin account."""
    
    print("=" * 60)
    print("    USER MANAGEMENT SYSTEM - ADMIN SETUP")
    print("=" * 60)
    
    # Create admin account
    if not create_default_admin():
        print("\n❌ Failed to create admin account!")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ ADMIN SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\n📱 Next Steps:")
    print("   1. Access the admin portal: http://localhost:3000/admin")
    print("   2. Login with the credentials above")
    print("   3. Set up MFA for enhanced security")
    print("   4. Change the default password")
    print("   5. Review and configure system settings")
    print("")

if __name__ == "__main__":
    main()
