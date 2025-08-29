from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import os
import uuid
from typing import Optional

from core.database import get_db
from schemas.user import UserResponse, UserUpdate
from services.user_service import user_service
from services.auth_service import get_current_active_user_dependency
from models.user import User

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user_dependency)
):
    """
    Get current user's profile information.
    """
    return UserResponse.model_validate(current_user)

@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """
    Update current user's profile information.
    
    - **first_name**: First name (max 100 characters)
    - **last_name**: Last name (max 100 characters)
    - **year_of_birth**: Birth year (1900-2024)
    - **description**: Profile description (max 1000 characters)
    - **avatar_url**: URL or path to user's avatar image
    """
    updated_user = user_service.update_user(db, current_user.id, user_update)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return UserResponse.model_validate(updated_user)

@router.post("/me/avatar", response_model=dict)
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user_dependency)
):
    """
    Upload and update user's avatar image.
    
    Accepts image files (jpg, jpeg, png, gif) up to 5MB.
    """
    # Validate file type
    allowed_types = {"image/jpeg", "image/jpg", "image/png", "image/gif"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files (JPG, PNG, GIF) are allowed"
        )
    
    # Read file content and validate size (5MB max)
    content = await file.read()
    max_size = 5 * 1024 * 1024  # 5MB
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 5MB"
        )
    
    # Create uploads directory if it doesn't exist
    upload_dir = "/app/uploads/avatars"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
    unique_filename = f"{current_user.id}_{uuid.uuid4().hex[:8]}.{file_extension}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save the file
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Update user's avatar URL
        avatar_url = f"/static/avatars/{unique_filename}"
        user_update = UserUpdate(avatar_url=avatar_url)
        updated_user = user_service.update_user(db, current_user.id, user_update)
        
        return {
            "message": "Avatar uploaded successfully",
            "avatar_url": avatar_url,
            "user": UserResponse.model_validate(updated_user)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
