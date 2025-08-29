from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.auth import router as auth_router
from api.v1.users import router as users_router
from api.mfa import router as mfa_router
from api.admin import router as admin_router  
from api.library import router as library_router
from api.notifications import router as notifications_router
from core.config import settings
from core.database import engine
from models import user, mfa, library, notification
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create database tables
try:
    from core.database import Base
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {str(e)}")

app = FastAPI(
    title=getattr(settings, 'PROJECT_NAME', 'User Management System'),
    version=getattr(settings, 'VERSION', '1.0.0'),
    description="Enhanced User Management System with MFA, Admin Portal, and Library Management",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
api_prefix = getattr(settings, 'API_V1_STR', '/api/v1')

app.include_router(auth_router, prefix=api_prefix, tags=["Authentication"])
app.include_router(users_router, prefix=f"{api_prefix}/users", tags=["Users"])
app.include_router(mfa_router, prefix=api_prefix, tags=["Multi-Factor Authentication"])
app.include_router(admin_router, prefix=api_prefix, tags=["Admin"])
app.include_router(library_router, prefix=api_prefix, tags=["Library"])
app.include_router(notifications_router, prefix=api_prefix, tags=["Notifications"])

# Mount static files for uploads
uploads_dir = "/app/uploads"
os.makedirs(f"{uploads_dir}/avatars", exist_ok=True)
os.makedirs(f"{uploads_dir}/book_covers", exist_ok=True)

try:
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory=uploads_dir), name="static")
    logger.info("Static files mounted successfully")
except ImportError:
    logger.warning("StaticFiles not available, skipping static file mounting")

@app.get("/")
def read_root():
    return {
        "message": "Enhanced User Management Service with MFA and Library Management",
        "version": getattr(settings, 'VERSION', '1.0.0'),
        "features": [
            "Multi-Factor Authentication (TOTP)",
            "Role-based Access Control",
            "Admin Portal with User Management",
            "Library Management System",
            "Email Notifications",
            "User Deletion with Audit Trail"
        ],
        "docs_url": "/docs",
        "admin_email": "uynhhuc810@gmail.com"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy", 
        "service": "enhanced-user-management",
        "features": {
            "mfa": True,
            "admin_portal": True,
            "library_management": True,
            "notifications": True,
            "email": True
        }
    }
