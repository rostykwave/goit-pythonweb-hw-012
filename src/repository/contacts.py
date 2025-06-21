from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.schemas import ContactCreate, ContactUpdate

from datetime import date, timedelta

class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(self, skip: int, limit: int, user_id: int) -> List[Contact]:
        stmt = select(Contact).filter_by(user_id=user_id).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int) -> Contact | None:
        stmt = select(Contact).filter_by(id=contact_id)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactCreate, user_id: int) -> Contact:
        contact = Contact(**body.model_dump(exclude_unset=True), user_id=user_id)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(self, contact_id: int, body: ContactUpdate) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            for field, value in body.model_dump(exclude_unset=True).items():
                setattr(contact, field, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int) -> Contact | None:
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
        stmt = select(Contact).where(
            (Contact.user_id == user_id) &
            ((Contact.first_name.ilike(f"%{query}%")) |
             (Contact.last_name.ilike(f"%{query}%")) |
             (Contact.email.ilike(f"%{query}%")))
        ).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()
    
    async def get_upcoming_birthdays(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Contact]:
        today = date.today()
        next_week = today + timedelta(days=7)
        
        stmt = select(Contact).where(
            (Contact.user_id == user_id) &
            (((Contact.birth_date.month == today.month) & 
              (Contact.birth_date.day >= today.day)) |
            ((Contact.birth_date.month == next_week.month) & 
            (Contact.birth_date.day <= next_week.day)))
        ).offset(skip).limit(limit)
    
        
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()