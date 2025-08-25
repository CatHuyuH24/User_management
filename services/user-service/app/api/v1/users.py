from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.session import get_db
from schemas.user import UserResponse, UserUpdate
from services.user_service import user_service
from api.v1.auth import get_current_user
from models.user import User

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's profile information.
    """
    return UserResponse.from_orm(current_user)

@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update current user's profile information.
    
    - **first_name**: First name (max 100 characters)
    - **last_name**: Last name (max 100 characters)
    - **year_of_birth**: Birth year (1900-2024)
    - **description**: Profile description (max 1000 characters)
    """
    updated_user = user_service.update_user(db, current_user.id, user_update)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.from_orm(updated_user)
