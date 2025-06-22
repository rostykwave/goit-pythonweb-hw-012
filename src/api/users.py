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
    
    Args:
        current_user (User): Current authenticated user
        
    Returns:
        UserResponse: Current user information
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
    
    Args:
        file (UploadFile): Image file for avatar
        current_user (User): Current authenticated user
        db (AsyncSession): Database session dependency
        
    Returns:
        UserResponse: Updated user information with new avatar URL
        
    Raises:
        HTTPException: If file upload or processing fails
    """
    user_service = UserService(db)
    updated_user = await user_service.update_avatar(current_user.id, file)
    
    # Clear cache after avatar update
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
    """Get all users - admin only endpoint."""
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
    """Update user role - admin only endpoint."""
    user_service = UserService(db)
    user = await user_service.update_user_role(user_id, role)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user