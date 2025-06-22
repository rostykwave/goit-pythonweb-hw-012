from datetime import datetime, timedelta, UTC
from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.database.db import get_db
from src.database.models import User
from src.conf.config import config
from src.services.users import UserService

from src.services.cache import cache_service

class Hash:
    """Password hashing utility class."""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        Verify plain password against hashed password.
        
        Args:
            plain_password (str): Plain text password
            hashed_password (str): Hashed password from database
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Hash plain password.
        
        Args:
            password (str): Plain text password
            
        Returns:
            str: Hashed password
        """
        return self.pwd_context.hash(password)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def create_access_token(data: dict, expires_delta: Optional[int] = None):
    """
    Create JWT access token.
    
    Args:
        data (dict): Token payload data
        expires_delta (int, optional): Token expiration time in seconds
        
    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=config.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM
    )
    return encoded_jwt

def create_email_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    return token

async def get_email_from_token(token: str, action_type: str = None):
    try:
        payload = jwt.decode(
            token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM]
        )
        email = payload["sub"]
        
        if action_type and payload.get("action") != action_type:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token type",
            )
            
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid token for email verification",
        )
    
async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    """
    Get current user with Redis caching.
    
    Args:
        token (str): JWT access token
        db (AsyncSession): Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Try to get user from cache first
    cached_user_data = await cache_service.get_user(username)
    if cached_user_data:
        # Convert dict back to User model
        user = User(**cached_user_data)
        return user
    
    # Try to get user from cache first
    cached_user_data = await cache_service.get_user(username)
    if cached_user_data:
        try:
            # Validate cached data structure
            required_fields = ["id", "username", "email", "confirmed"]
            if all(field in cached_user_data for field in required_fields):
                user = User(**cached_user_data)
                return user
            else:
                # Invalid cache data, delete it
                await cache_service.delete_user(username)
        except Exception:
            # Invalid cached data, delete it
            await cache_service.delete_user(username)

    # If not in cache, get from database
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception

    # Cache the user data for future requests
    user_dict = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "confirmed": user.confirmed,
        "avatar": user.avatar,
        # Remove hashed_password from cache for security
    }
    await cache_service.set_user(username, user_dict)

    return user