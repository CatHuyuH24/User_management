# User Management System API Routes
from .mfa import router as mfa_router
from .admin import router as admin_router
from .library import router as library_router
from .notifications import router as notifications_router

__all__ = [
    "mfa_router",
    "admin_router", 
    "library_router",
    "notifications_router"
]
