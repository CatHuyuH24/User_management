from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.config import settings
from core.database import get_db
from models.user import User, UserRole
from schemas.user import TokenData, UserRole as SchemaUserRole
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token scheme
security = HTTPBearer()

class AuthService:
    """Service for handling authentication and authorization"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = settings.ALGORITHM
        self.access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = getattr(settings, 'REFRESH_TOKEN_EXPIRE_DAYS', 7)
        self.mfa_token_expire_minutes = getattr(settings, 'MFA_TOKEN_EXPIRE_MINUTES', 10)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}")
            return False
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def authenticate_user(self, db: Session, identifier: str, password: str, is_email: bool = True) -> Union[User, bool]:
        """Authenticate user with email or username and password"""
        try:
            if is_email:
                user = db.query(User).filter(User.email == identifier).first()
            else:
                user = db.query(User).filter(User.username == identifier).first()
                
            if not user:
                return False
            if not user.is_active:
                return False
            if not self.verify_password(password, user.hashed_password):
                return False
            return user
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return False
            
    def authenticate_user_flexible(self, db: Session, username_or_email: str, password: str) -> Union[User, bool]:
        """Authenticate user with either username or email"""
        try:
            # First try email
            user = db.query(User).filter(User.email == username_or_email).first()
            if not user:
                # Try username
                user = db.query(User).filter(User.username == username_or_email).first()
                
            if not user:
                return False
            if not user.is_active:
                return False
            if not self.verify_password(password, user.hashed_password):
                return False
            return user
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return False
    
    def create_access_token(
        self, 
        data: dict, 
        expires_delta: Optional[timedelta] = None,
        token_type: str = "access"
    ) -> str:
        """Create JWT token"""
        try:
            to_encode = data.copy()
            
            if expires_delta:
                expire = datetime.utcnow() + expires_delta
            else:
                if token_type == "mfa":
                    expire = datetime.utcnow() + timedelta(minutes=self.mfa_token_expire_minutes)
                else:
                    expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
            
            to_encode.update({
                "exp": expire,
                "type": token_type,
                "iat": datetime.utcnow()
            })
            
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating access token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create access token"
            )
    
    def create_mfa_token(self, user_id: int, email: str) -> str:
        """Create temporary MFA token for two-step authentication"""
        data = {
            "sub": str(user_id),
            "email": email,
            "mfa_pending": True
        }
        return self.create_access_token(data, token_type="mfa")
    
    def verify_token(self, token: str, expected_type: str = "access") -> Optional[TokenData]:
        """Verify and decode JWT token with enhanced error handling"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            token_type = payload.get("type", "access")
            if token_type != expected_type:
                logger.warning(f"Token type mismatch: expected {expected_type}, got {token_type}")
                return None
            
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            role: str = payload.get("role")
            username: str = payload.get("username")
            
            if user_id is None:
                logger.warning("Token missing user ID")
                return None
            
            # Check if token is expired (additional check)
            exp = payload.get("exp")
            if exp:
                current_time = datetime.utcnow().timestamp()
                if current_time > exp:
                    logger.info(f"Token expired for user {user_id}")
                    return None
            
            token_data = TokenData(
                user_id=int(user_id),
                username=username,
                email=email,
                role=SchemaUserRole(role) if role else None
            )
            return token_data
            
        except jwt.ExpiredSignatureError:
            logger.info("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {str(e)}")
            return None
        except JWTError as e:
            logger.error(f"JWT Error: {str(e)}")
            return None
        except ValueError as e:
            logger.error(f"Token validation error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error verifying token: {str(e)}")
            return None
    
    def get_current_user(self, db: Session, credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
        """Get current authenticated user from token with enhanced error handling"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        token_expired_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            token_data = self.verify_token(credentials.credentials)
            if token_data is None:
                logger.warning(f"Token validation failed")
                raise credentials_exception
            
            user = db.query(User).filter(User.id == token_data.user_id).first()
            if user is None:
                logger.warning(f"User not found for token user_id: {token_data.user_id}")
                raise credentials_exception
            
            if not user.is_active:
                logger.warning(f"Inactive user attempted access: {user.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Inactive user"
                )
            
            # Update last_login timestamp
            user.last_login = datetime.utcnow()
            db.commit()
            
            return user
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Unexpected error getting current user: {str(e)}")
            raise credentials_exception
    
    def get_current_active_user(self, db: Session, credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
        """Get current active user"""
        user = self.get_current_user(db, credentials)
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )
        return user
    
    def require_role(self, required_roles: Union[UserRole, list[UserRole]]):
        """Decorator to require specific roles"""
        if isinstance(required_roles, UserRole):
            required_roles = [required_roles]
        
        def role_checker(db: Session, credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
            user = self.get_current_active_user(db, credentials)
            
            if user.role not in required_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions"
                )
            
            return user
        
        return role_checker
    
    def require_admin(self, db: Session, credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
        """Require admin or super_admin role"""
        user = self.get_current_active_user(db, credentials)
        
        # Check against string values since role is stored as string in DB
        if user.role not in ["admin", "super_admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        return user
    
    def require_super_admin(self, db: Session, credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
        """Require super_admin role"""
        user = self.get_current_active_user(db, credentials)
        
        # Check against string value since role is stored as string in DB
        if user.role != "super_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Super admin access required"
            )
        
        return user
    
    def verify_mfa_token(self, token: str) -> Optional[dict]:
        """Verify MFA token and return user data"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if it's an MFA token
            if payload.get("type") != "mfa" or not payload.get("mfa_pending"):
                return None
            
            return {
                "user_id": int(payload.get("sub")),
                "email": payload.get("email")
            }
            
        except JWTError as e:
            logger.error(f"MFA JWT Error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error verifying MFA token: {str(e)}")
            return None
    
    def create_full_access_token(self, user: User) -> str:
        """Create full access token after successful MFA"""
        data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value if hasattr(user.role, 'value') else str(user.role),
            "username": user.username,
            "mfa_verified": user.mfa_enabled
        }
        return self.create_access_token(data)
    
    def refresh_token(self, db: Session, current_user: User) -> str:
        """Refresh access token for current user"""
        return self.create_full_access_token(current_user)

# Dependency functions for FastAPI
def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """FastAPI dependency to get current user"""
    return auth_service.get_current_user(db, credentials)

def get_current_active_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: Session = Depends(get_db)
) -> User:
    """FastAPI dependency to get current active user"""
    return auth_service.get_current_active_user(db, credentials)

def require_admin_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """FastAPI dependency to require admin role"""
    user = auth_service.get_current_active_user(db, credentials)
    # Check against string values since role is stored as string in DB
    if user.role not in ["admin", "super_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user

# Create singleton instance
auth_service = AuthService()
