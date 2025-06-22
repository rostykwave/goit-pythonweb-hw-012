from fastapi import APIRouter, Depends, UploadFile, File, Request, HTTPException
from src.schemas import User
from src.services.auth import get_current_user, get_current_admin
from src.services.users import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.database.models import UserRole
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)

@router.get("/me", response_model=User, description="No more than 10 requests per minute")
@limiter.limit("10/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Get current user information.
    
    This endpoint allows authenticated users to retrieve their own profile information.
    Rate limited to 10 requests per minute to prevent abuse.
    
    Args:
        request (Request): HTTP request object for rate limiting
        user (User): Current authenticated user from dependency injection
        
    Returns:
        User: Current user information including id, username, email, avatar, etc.
        
    Raises:
        HTTPException: 401 if user is not authenticated
        HTTPException: 429 if rate limit is exceeded (10 requests per minute)
    """
    return user

@router.patch("/avatar", response_model=User)
async def update_avatar(
    file: UploadFile = File(),
    current_user: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user avatar image.
    
    This endpoint allows admin users to update their avatar image.
    The uploaded image is processed and stored, with the avatar URL updated in the database.
    Cache is cleared after successful update to ensure fresh data retrieval.
    
    Args:
        file (UploadFile): Image file for avatar upload (JPEG, PNG, etc.)
        current_user (User): Current authenticated admin user
        db (AsyncSession): Database session dependency for data operations
        
    Returns:
        User: Updated user information with new avatar URL
        
    Raises:
        HTTPException: 401 if user is not authenticated
        HTTPException: 403 if user is not an admin
        HTTPException: 400 if file upload fails or invalid file format
        HTTPException: 500 if database error occurs during avatar update
    """
    user_service = UserService(db)
    updated_user = await user_service.update_avatar(current_user.id, file)
    
    from src.services.cache import cache_service
    await cache_service.delete_user(current_user.username)
    
    return updated_user

@router.get("/", response_model=list[User], description="Get all users (Admin only)")
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Get all users in the system.
    
    This endpoint is restricted to admin users only and returns a paginated list
    of all registered users in the system.
    
    Args:
        skip (int, optional): Number of records to skip for pagination. Defaults to 0.
        limit (int, optional): Maximum number of records to return. Defaults to 100.
        db (AsyncSession): Database session dependency for data operations
        current_admin (User): Current authenticated admin user
        
    Returns:
        list[User]: List of user objects with pagination applied
        
    Raises:
        HTTPException: 401 if user is not authenticated
        HTTPException: 403 if user is not an admin
        HTTPException: 500 if database error occurs during query
    """
    user_service = UserService(db)
    users = await user_service.get_all_users(skip, limit)
    return users

@router.patch("/{user_id}/role", response_model=User, description="Update user role (Admin only)")
async def update_user_role(
    user_id: int,
    role: UserRole,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Update user role in the system.
    
    This endpoint allows admin users to change the role of any user in the system.
    Available roles are defined in the UserRole enum (USER, ADMIN).
    
    Args:
        user_id (int): ID of the user whose role should be updated
        role (UserRole): New role to assign to the user (USER or ADMIN)
        db (AsyncSession): Database session dependency for data operations
        current_admin (User): Current authenticated admin user
        
    Returns:
        User: Updated user information with new role
        
    Raises:
        HTTPException: 401 if user is not authenticated
        HTTPException: 403 if user is not an admin
        HTTPException: 404 if user with specified ID is not found
        HTTPException: 500 if database error occurs during role update
    """
    user_service = UserService(db)
    user = await user_service.update_user_role(user_id, role)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user