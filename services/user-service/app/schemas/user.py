from pydantic import BaseModel, EmailStr
from typing import Optional

# Schema for user creation
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

# Schema for user response
class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    year_of_birth: Optional[int] = None
    description: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        orm_mode = True

# Schema for user update
class UserUpdate(BaseModel):
    year_of_birth: Optional[int] = None
    description: Optional[str] = None

# Schema for token
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
