#!/usr/bin/env python3
"""
Comprehensive User Creation Script
Creates default admin and client users for the system.
"""

import asyncio
import sys
import os

# Add the services/user-service/app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services', 'user-service', 'app'))

from sqlalchemy.orm import Session
from core.database import SessionLocal, engine, Base
from models.user import User, UserRole
from services.auth_service import auth_service
from services.user_service import user_service
from schemas.user import UserCreate

# Default user account details
USERS_TO_CREATE = [
    {
        "username": "super",
        "email": "super@admin.com",
        "password": "SuperAdminPassword123!",
        "first_name": "Super",
        "last_name": "Admin",
        "role": UserRole.SUPER_ADMIN,
        "is_verified": True,
        "is_active": True,
        "description": "Super Administrator with full system access"
    },
    {
        "username": "client",
        "email": "client@example.com", 
        "password": "ClientPassword123?",
        "first_name": "Demo",
        "last_name": "Client",
        "role": UserRole.CLIENT,
        "is_verified": True,
        "is_active": True,
        "description": "Demo client user for testing purposes"
    }
]

def create_users():
    """Create all default users if they don't exist."""
    
    print("🚀 Setting up default user accounts...")
    
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
        users_created = 0
        users_existing = 0
        
        for user_data in USERS_TO_CREATE:
            # Check if user already exists
            existing_user = db.query(User).filter(
                (User.email == user_data["email"]) | 
                (User.username == user_data["username"])
            ).first()
            
            if existing_user:
                print(f"✅ User already exists: {user_data['username']} ({user_data['email']})")
                print(f"   Role: {existing_user.role.value}")
                print(f"   Active: {existing_user.is_active}")
                print(f"   Verified: {existing_user.is_verified}")
                users_existing += 1
                continue
            
            # Create user
            user_create = UserCreate(
                username=user_data["username"],
                email=user_data["email"],
                password=user_data["password"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"]
            )
            
            # Use user service to create user
            new_user = user_service.create_user(db, user_create)
            
            # Set additional properties
            new_user.role = user_data["role"].value  # Use .value to get the string value
            new_user.is_verified = user_data["is_verified"]
            new_user.is_active = user_data["is_active"]
            if user_data.get("description"):
                new_user.description = user_data["description"]
            
            db.commit()
            db.refresh(new_user)
            
            print(f"✅ User created successfully: {user_data['username']}")
            print(f"   Email: {user_data['email']}")
            print(f"   Password: {user_data['password']}")
            print(f"   Role: {new_user.role.value}")
            print(f"   Name: {user_data['first_name']} {user_data['last_name']}")
            users_created += 1
        
        print(f"\n📊 Summary:")
        print(f"   Users created: {users_created}")
        print(f"   Users existing: {users_existing}")
        print(f"   Total users: {users_created + users_existing}")
        
        if users_created > 0:
            print("\n⚠️  IMPORTANT: Change default passwords after first login!")
            print("⚠️  These accounts are for development/testing purposes.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating user accounts: {str(e)}")
        db.rollback()
        return False
        
    finally:
        db.close()

def main():
    """Main function to create all users."""
    
    print("=" * 60)
    print("    USER MANAGEMENT SYSTEM - USER SETUP")
    print("=" * 60)
    
    # Create user accounts
    if not create_users():
        print("\n❌ Failed to create user accounts!")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ USER SETUP COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\n📱 Next Steps:")
    print("   1. Access the application: http://localhost:3001")
    print("   2. Login with super admin credentials:")
    print("      - Username: super")
    print("      - Password: SuperAdminPassword123!")
    print("   3. Login with client credentials:")
    print("      - Username: client") 
    print("      - Password: ClientPassword123?")
    print("   4. Set up MFA for enhanced security")
    print("   5. Change default passwords")
    print("   6. Review and configure system settings")
    print("")

if __name__ == "__main__":
    main()
