from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate

class UserRepository:
    """Repository for user database operations."""

    def __init__(self, session: AsyncSession):
        """
        Initialize UserRepository.
        
        Args:
            session (AsyncSession): Database session
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Get user by email address.
        
        Args:
            email (str): User's email address
            
        Returns:
            User | None: User object if found, None otherwise
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Create new user in database.
        
        Args:
            body (UserCreate): User creation data
            avatar (str, optional): Avatar URL
            
        Returns:
            User: Created user object
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_avatar(self, user_id: int, avatar_url: str) -> User:
        """
        Update user avatar URL in database.
        
        Args:
            user_id (int): User ID
            avatar_url (str): New avatar URL
            
        Returns:
            User | None: Updated user object if found, None otherwise
        """
        user = await self.get_user_by_id(user_id)
        if user:
            user.avatar = avatar_url
            await self.db.commit()
            await self.db.refresh(user)
        return user
    
    async def confirmed_email(self, email: str) -> None:
        """
        Mark user email as confirmed.
        
        Args:
            email (str): User's email address
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()