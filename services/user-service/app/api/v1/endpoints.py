from fastapi import APIRouter

from api.v1 import auth, users

router = APIRouter()

# Include auth routes
router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Include user routes  
router.include_router(users.router, prefix="/users", tags=["users"])
