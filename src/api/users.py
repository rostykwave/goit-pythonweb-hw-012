from fastapi import APIRouter, Depends, UploadFile, File, Request
from src.schemas import User
from src.services.auth import get_current_user
from src.services.users import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
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
    current_user: User = Depends(get_current_user),
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
    user = await user_service.update_avatar(current_user.id, file)
    return user