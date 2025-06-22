from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

from src.repository.users import UserRepository
from src.schemas import UserCreate
from src.conf.config import config

from src.services.cache import cache_service
from src.database.models import UserRole 

class UserService:
    """Service for user-related operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize UserService.
        
        Args:
            db (AsyncSession): Database session
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Create new user account.
        
        Args:
            body (UserCreate): User creation data
            avatar (str, optional): Avatar URL
            
        Returns:
            User: Created user object
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        new_user = await self.repository.create_user(body, avatar)
    
        await cache_service.delete_user(body.username)
    
        return new_user

    async def get_user_by_id(self, user_id: int):
        """
        Get user by ID.
        
        Args:
            user_id (int): User ID
            
        Returns:
            User | None: User object if found, None otherwise
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Get user by username.
        
        Args:
            username (str): Username
            
        Returns:
            User | None: User object if found, None otherwise
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Get user by email address.
        
        Args:
            email (str): User's email address
            
        Returns:
            User | None: User object if found, None otherwise
        """
        return await self.repository.get_user_by_email(email)

    async def update_avatar(self, user_id: int, file):
        """
        Update user avatar URL.
        
        Args:
            user_id (int): User ID
            avatar_url (str): New avatar URL
            
        Returns:
            User | None: Updated user object if found, None otherwise
        """
        cloudinary.config(
            cloud_name=config.CLOUDINARY_NAME,
            api_key=config.CLOUDINARY_API_KEY,
            api_secret=config.CLOUDINARY_API_SECRET
        )
        
        upload_result = cloudinary.uploader.upload(
            file.file, 
            public_id=f"avatars/{user_id}",
            overwrite=True,
            resource_type="image"
        )
        
        avatar_url = cloudinary.utils.cloudinary_url(
            upload_result['public_id'], 
            version=upload_result['version']
        )[0]
        
        result = await self.repository.update_avatar(user_id, avatar_url)
            
        user = await self.repository.get_user_by_id(user_id)
        if user:
            await cache_service.delete_user(user.username)
        
        return result
    
    async def confirmed_email(self, email: str):
        """
        Confirm user email and clear cache.
        """
        user = await self.repository.get_user_by_email(email)
        if user:
            await cache_service.delete_user(user.username)
        
        return await self.repository.confirmed_email(email)
    
    async def update_user_password(self, email: str, new_password: str):
        """Update user password and clear cache."""
        user = await self.repository.get_user_by_email(email)
        if user:
            await cache_service.delete_user(user.username)
    
        return await self.repository.update_user_password(email, new_password)
    
    async def get_all_users(self, skip: int = 0, limit: int = 100):
        """Get all users (admin function)."""
        return await self.repository.get_all_users(skip, limit)
    
    async def update_user_role(self, user_id: int, role: UserRole):
        """Update user role (admin function)."""
        user = await self.repository.get_user_by_id(user_id)
        if user:
            await cache_service.delete_user(user.username)
        
        return await self.repository.update_user_role(user_id, role)