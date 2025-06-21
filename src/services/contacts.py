from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas import ContactCreate, ContactUpdate

class ContactService:
    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactCreate, user_id: int):
        return await self.repository.create_contact(body, user_id)

    async def get_contacts(self, skip: int, limit: int, user_id: int):
        return await self.repository.get_contacts(skip, limit, user_id)

    async def get_contact(self, contact_id: int):
        return await self.repository.get_contact_by_id(contact_id)

    async def update_contact(self, contact_id: int, body: ContactUpdate):
        return await self.repository.update_contact(contact_id, body)

    async def remove_contact(self, contact_id: int):
        return await self.repository.remove_contact(contact_id)
    
    async def search_contacts(self, query: str, user_id: int, skip: int = 0, limit: int = 100):
        return await self.repository.search_contacts(query, user_id, skip, limit)

    async def get_upcoming_birthdays(self, user_id: int, skip: int = 0, limit: int = 100):
        return await self.repository.get_upcoming_birthdays(user_id, skip, limit)