from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import ContactCreate, ContactUpdate, ContactResponse, User
from src.services.contacts import ContactService
from src.services.auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get paginated list of contacts for the current user.
    
    Args:
        skip (int): Number of records to skip for pagination
        limit (int): Maximum number of records to return
        db (AsyncSession): Database session dependency
        current_user (User): Current authenticated user
        
    Returns:
        List[ContactResponse]: List of contact objects
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, current_user.id)
    return contacts

@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific contact by ID.
    
    Args:
        contact_id (int): ID of the contact to retrieve
        db (AsyncSession): Database session dependency
        current_user (User): Current authenticated user
        
    Returns:
        ContactResponse: Contact object
        
    Raises:
        HTTPException: 404 if contact not found or doesn't belong to user
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id)
    if contact is None or contact.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new contact for the current user.
    
    Args:
        body (ContactCreate): Contact data to create including name, email, phone, etc.
        db (AsyncSession): Database session dependency
        current_user (User): Current authenticated user
        
    Returns:
        ContactResponse: The created contact object
        
    Raises:
        HTTPException: If contact creation fails
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, current_user.id)

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactUpdate, 
    contact_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing contact by ID.
    
    Args:
        body (ContactUpdate): Updated contact data
        contact_id (int): ID of the contact to update
        db (AsyncSession): Database session dependency
        current_user (User): Current authenticated user
        
    Returns:
        ContactResponse: The updated contact object
        
    Raises:
        HTTPException: 404 if contact not found or doesn't belong to user
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body)
    if contact is None or contact.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact

@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
    contact_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a contact by ID.
    
    Args:
        contact_id (int): ID of the contact to delete
        db (AsyncSession): Database session dependency
        current_user (User): Current authenticated user
        
    Returns:
        ContactResponse: The deleted contact object
        
    Raises:
        HTTPException: 404 if contact not found or doesn't belong to user
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id)
    if contact is None or contact.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return await contact_service.remove_contact(contact_id)

@router.get("/search/", response_model=List[ContactResponse])
async def search_contacts(
    q: str, 
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search contacts by name, email, or phone number.
    
    Args:
        q (str): Search query string
        skip (int): Number of records to skip for pagination
        limit (int): Maximum number of records to return
        db (AsyncSession): Database session dependency
        current_user (User): Current authenticated user
        
    Returns:
        List[ContactResponse]: List of matching contact objects
    """
    contact_service = ContactService(db)
    contacts = await contact_service.search_contacts(q, current_user.id, skip, limit)
    return contacts

@router.get("/birthdays/", response_model=List[ContactResponse])
async def get_upcoming_birthdays(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get contacts with upcoming birthdays (within the next 7 days).
    
    Args:
        skip (int): Number of records to skip for pagination
        limit (int): Maximum number of records to return
        db (AsyncSession): Database session dependency
        current_user (User): Current authenticated user
        
    Returns:
        List[ContactResponse]: List of contacts with upcoming birthdays
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_upcoming_birthdays(current_user.id, skip, limit)
    return contacts