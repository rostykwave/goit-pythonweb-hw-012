from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.contacts import ContactRepository
from src.schemas import ContactCreate, ContactUpdate

class ContactService:
    """
    Service layer for contact management operations.
    
    This class handles business logic for contact operations including
    CRUD operations, search functionality, and birthday reminders.
    """
    def __init__(self, db: AsyncSession):
        """
        Initialize ContactService with database session.
        
        Args:
            db (AsyncSession): Database session for operations
        """
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactCreate, user_id: int):
        """
        Create a new contact for a specific user.
        
        Args:
            body (ContactCreate): Contact data to create
            user_id (int): ID of the user who owns the contact
            
        Returns:
            Contact: Created contact object
        """
        return await self.repository.create_contact(body, user_id)

    async def get_contacts(self, skip: int, limit: int, user_id: int):
        """
        Get paginated list of contacts for a specific user.
        
        Args:
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            user_id (int): ID of the user whose contacts to retrieve
            
        Returns:
            List[Contact]: List of contact objects
        """
        return await self.repository.get_contacts(skip, limit, user_id)

    async def get_contact(self, contact_id: int):
        """
        Get a specific contact by ID.
        
        Args:
            contact_id (int): ID of the contact to retrieve
            
        Returns:
            Contact | None: Contact object if found, None otherwise
        """
        return await self.repository.get_contact_by_id(contact_id)

    async def update_contact(self, contact_id: int, body: ContactUpdate):
        """
        Update an existing contact.
        
        Args:
            contact_id (int): ID of the contact to update
            body (ContactUpdate): Updated contact data
            
        Returns:
            Contact | None: Updated contact object if found, None otherwise
        """
        return await self.repository.update_contact(contact_id, body)

    async def remove_contact(self, contact_id: int):
        """
        Remove a contact by ID.
        
        Args:
            contact_id (int): ID of the contact to remove
            
        Returns:
            Contact | None: Removed contact object if found, None otherwise
        """
        return await self.repository.remove_contact(contact_id)
    
    async def search_contacts(self, query: str, user_id: int, skip: int = 0, limit: int = 100):
        """
        Search contacts by name or email.
        
        Args:
            query (str): Search query string
            user_id (int): ID of the user whose contacts to search
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.
            
        Returns:
            List[Contact]: List of matching contact objects
        """
        return await self.repository.search_contacts(query, user_id, skip, limit)

    async def get_upcoming_birthdays(self, user_id: int, skip: int = 0, limit: int = 100):
        """
        Get contacts with upcoming birthdays (next 7 days).
        
        Args:
            user_id (int): ID of the user whose contacts to check
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records to return. Defaults to 100.
            
        Returns:
            List[Contact]: List of contacts with upcoming birthdays
        """
        return await self.repository.get_upcoming_birthdays(user_id, skip, limit)