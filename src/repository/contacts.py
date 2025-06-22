from typing import List
from sqlalchemy import select, extract, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.schemas import ContactCreate, ContactUpdate

from datetime import date, timedelta

class ContactRepository:
    """Repository for contact database operations."""

    def __init__(self, session: AsyncSession):
        """
        Initialize ContactRepository.
        
        Args:
            session (AsyncSession): Database session
        """
        self.db = session

    async def get_contacts(self, skip: int, limit: int, user_id: int) -> List[Contact]:
        """
        Get paginated contacts from database.
        
        Args:
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            user_id (int): User ID
            
        Returns:
            List[Contact]: List of contact objects
        """
        stmt = select(Contact).filter_by(user_id=user_id).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int) -> Contact | None:
        """
        Get contact by ID from database.
        
        Args:
            contact_id (int): Contact ID
            
        Returns:
            Contact | None: Contact object if found, None otherwise
        """
        stmt = select(Contact).filter_by(id=contact_id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactCreate, user_id: int) -> Contact:
        """
        Create new contact in database.
        
        Args:
            body (ContactCreate): Contact creation data
            user_id (int): User ID
            
        Returns:
            Contact: Created contact object
        """
        contact = Contact(**body.model_dump(exclude_unset=True), user_id=user_id)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(self, contact_id: int, body: ContactUpdate) -> Contact | None:
        """
        Update contact in database.
        
        Args:
            contact_id (int): Contact ID
            body (ContactUpdate): Contact update data
            
        Returns:
            Contact | None: Updated contact object if found, None otherwise
        """
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            for field, value in body.model_dump(exclude_unset=True).items():
                setattr(contact, field, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int) -> Contact | None:
        """
        Remove contact from database.
        
        Args:
            contact_id (int): Contact ID
            
        Returns:
            Contact | None: Removed contact object if found, None otherwise
        """
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def get_contacts_by_ids(self, contact_ids: list[int]) -> list[Contact]:
        stmt = select(Contact).where(Contact.id.in_(contact_ids))
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def search_contacts(self, query: str, user_id: int, skip: int = 0, limit: int = 100) -> List[Contact]:
        """
        Search contacts in database by query.
        
        Args:
            query (str): Search query string
            user_id (int): User ID
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[Contact]: List of matching contact objects
        """
        stmt = select(Contact).where(
            (Contact.user_id == user_id) &
            ((Contact.first_name.ilike(f"%{query}%")) |
             (Contact.last_name.ilike(f"%{query}%")) |
             (Contact.email.ilike(f"%{query}%")))
        ).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()
    
    async def get_upcoming_birthdays(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Contact]:
        """
        Get contacts with upcoming birthdays from database.
        
        Args:
            user_id (int): User ID
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            
        Returns:
            List[Contact]: List of contacts with upcoming birthdays
        """
        today = date.today()
        next_week = today + timedelta(days=7)
        
        stmt = select(Contact).where(
            and_(
                Contact.user_id == user_id,
                or_(
                    and_(
                        extract('month', Contact.birth_date) == today.month,
                        extract('day', Contact.birth_date) >= today.day
                    ),
                    and_(
                        extract('month', Contact.birth_date) == next_week.month,
                        extract('day', Contact.birth_date) <= next_week.day
                    )
                )
            )
        ).offset(skip).limit(limit)
    
        
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()