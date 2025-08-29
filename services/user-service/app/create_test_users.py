#!/usr/bin/env python3
"""
Script to create default test users in Docker environment
Creates:
1. Super Admin: username="super", password="SuperAdminPassword123!"
2. Client: username="client", password="ClientPassword123?"
"""
import sys
import os
import logging
from pathlib import Path

# Add the app directory to Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

try:
    from sqlalchemy.orm import Session
    from core.database import SessionLocal, engine, Base
    from models.user import User, UserRole
    from services.auth_service import auth_service
    from datetime import datetime
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure all dependencies are installed")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def create_database_tables():
    """Create database tables if they don't exist"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created/verified")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating database tables: {str(e)}")
        return False

def create_user_if_not_exists(db: Session, username: str, email: str, password: str, 
                              first_name: str, last_name: str, role: UserRole) -> User:
    """Create a user if it doesn't already exist"""
    
    # Check if user exists by username or email
    existing_user = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    
    if existing_user:
        logger.info(f"📋 User {username} already exists (ID: {existing_user.id})")
        # Update role if different
        if existing_user.role != role:
            existing_user.role = role
            existing_user.is_verified = True
            existing_user.is_active = True
            db.commit()
            logger.info(f"✅ Updated {username} role to {role.value}")
        return existing_user
    
    # Create new user
    hashed_password = auth_service.get_password_hash(password)
    
    new_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        first_name=first_name,
        last_name=last_name,
        role=role,
        is_active=True,
        is_verified=True,
        mfa_enabled=False,
        created_at=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"✅ Created {role.value}: {username} (ID: {new_user.id})")
    return new_user

def create_default_users():
    """Create default super admin and client users"""
    
    logger.info("🚀 Starting user creation process...")
    
    # Create database tables
    if not create_database_tables():
        return False
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create Super Admin
        super_admin = create_user_if_not_exists(
            db=db,
            username="super",
            email="super@admin.com",
            password="SuperAdminPassword123!",
            first_name="Super",
            last_name="Admin",
            role=UserRole.SUPER_ADMIN
        )
        
        # Create Client User
        client_user = create_user_if_not_exists(
            db=db,
            username="client",
            email="client@example.com", 
            password="ClientPassword123?",
            first_name="Client",
            last_name="First",
            role=UserRole.CLIENT
        )
        
        logger.info("=" * 60)
        logger.info("DEFAULT USERS CREATED SUCCESSFULLY!")
        logger.info("=" * 60)
        logger.info(f"🔑 Super Admin:")
        logger.info(f"   Username: super")
        logger.info(f"   Email: super@admin.com")
        logger.info(f"   Password: SuperAdminPassword123!")
        logger.info(f"   Role: {super_admin.role.value}")
        logger.info(f"   ID: {super_admin.id}")
        logger.info("")
        logger.info(f"👤 Client User:")
        logger.info(f"   Username: client")
        logger.info(f"   Email: client@example.com")
        logger.info(f"   Password: ClientPassword123?")
        logger.info(f"   Role: {client_user.role.value}")
        logger.info(f"   ID: {client_user.id}")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating users: {str(e)}")
        db.rollback()
        return False
        
    finally:
        db.close()

def verify_users():
    """Verify that users can be authenticated"""
    
    logger.info("\n🔍 Verifying user authentication...")
    
    db = SessionLocal()
    
    try:
        # Test Super Admin authentication
        super_admin = auth_service.authenticate_user_flexible(
            db, "super", "SuperAdminPassword123!"
        )
        
        if super_admin:
            logger.info(f"✅ Super Admin authentication verified (Role: {super_admin.role.value})")
        else:
            logger.error("❌ Super Admin authentication failed")
            return False
        
        # Test Client authentication
        client = auth_service.authenticate_user_flexible(
            db, "client", "ClientPassword123?"
        )
        
        if client:
            logger.info(f"✅ Client authentication verified (Role: {client.role.value})")
        else:
            logger.error("❌ Client authentication failed")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error verifying users: {str(e)}")
        return False
        
    finally:
        db.close()

def main():
    """Main function"""
    
    print("=" * 60)
    print("    USER MANAGEMENT SYSTEM - USER CREATION")
    print("=" * 60)
    
    # Create users
    if not create_default_users():
        logger.error("❌ FAILED TO CREATE USERS")
        return 1
    
    # Verify users
    if not verify_users():
        logger.error("❌ FAILED TO VERIFY USERS")
        return 1
    
    print("\n" + "=" * 60)
    print("✅ USER CREATION COMPLETED SUCCESSFULLY!")
    print("=" * 60)
    print("\n📱 Next Steps:")
    print("   1. Access the application: http://localhost:3001")
    print("   2. Login with the credentials above")
    print("   3. Test both super admin and client functionality")
    print("   4. Run test suites to verify everything works")
    print("")
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
