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
    
    This endpoint retrieves all contacts belonging to the currently authenticated user
    with support for pagination through skip and limit parameters.
    
    Args:
        skip (int, optional): Number of records to skip for pagination. Defaults to 0.
        limit (int, optional): Maximum number of records to return. Defaults to 100.
        db (AsyncSession): Database session dependency injected by FastAPI.
        current_user (User): Current authenticated user injected by dependency.
        
    Returns:
        List[ContactResponse]: List of contact objects belonging to the user.
        
    Raises:
        HTTPException: 401 if user is not authenticated.
        HTTPException: 500 if database error occurs.
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
    
    Retrieves a single contact by its unique identifier. The contact must belong
    to the currently authenticated user.
    
    Args:
        contact_id (int): Unique identifier of the contact to retrieve.
        db (AsyncSession): Database session dependency injected by FastAPI.
        current_user (User): Current authenticated user injected by dependency.
        
    Returns:
        ContactResponse: The requested contact object with all its details.
        
    Raises:
        HTTPException: 404 if contact not found or doesn't belong to the user.
        HTTPException: 401 if user is not authenticated.
        HTTPException: 422 if contact_id is not a valid integer.
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
    
    Creates a new contact record with the provided information and associates it
    with the currently authenticated user.
    
    Args:
        body (ContactCreate): Contact creation data including first_name, last_name,
                            email, phone_number, birthday, and additional_data.
        db (AsyncSession): Database session dependency injected by FastAPI.
        current_user (User): Current authenticated user injected by dependency.
        
    Returns:
        ContactResponse: The newly created contact object with generated ID and timestamps.
        
    Raises:
        HTTPException: 401 if user is not authenticated.
        HTTPException: 422 if request body validation fails.
        HTTPException: 400 if contact with same email already exists for user.
        HTTPException: 500 if database error occurs during creation.
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
    
    Updates the specified contact with new information. The contact must belong
    to the currently authenticated user. Only provided fields will be updated.
    
    Args:
        body (ContactUpdate): Updated contact data with optional fields for
                            first_name, last_name, email, phone_number, birthday,
                            and additional_data.
        contact_id (int): Unique identifier of the contact to update.
        db (AsyncSession): Database session dependency injected by FastAPI.
        current_user (User): Current authenticated user injected by dependency.
        
    Returns:
        ContactResponse: The updated contact object with modified fields and
                        updated timestamp.
        
    Raises:
        HTTPException: 404 if contact not found or doesn't belong to the user.
        HTTPException: 401 if user is not authenticated.
        HTTPException: 422 if contact_id is not valid or body validation fails.
        HTTPException: 400 if updated email conflicts with existing contact.
        HTTPException: 500 if database error occurs during update.
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
    
    Permanently removes the specified contact from the database. The contact
    must belong to the currently authenticated user.
    
    Args:
        contact_id (int): Unique identifier of the contact to delete.
        db (AsyncSession): Database session dependency injected by FastAPI.
        current_user (User): Current authenticated user injected by dependency.
        
    Returns:
        ContactResponse: The deleted contact object for confirmation purposes.
        
    Raises:
        HTTPException: 404 if contact not found or doesn't belong to the user.
        HTTPException: 401 if user is not authenticated.
        HTTPException: 422 if contact_id is not a valid integer.
        HTTPException: 500 if database error occurs during deletion.
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
    
    Performs a text search across contact fields (first_name, last_name, email,
    phone_number) for the currently authenticated user. Search is case-insensitive
    and supports partial matches.
    
    Args:
        q (str): Search query string to match against contact fields.
        skip (int, optional): Number of records to skip for pagination. Defaults to 0.
        limit (int, optional): Maximum number of records to return. Defaults to 100.
        db (AsyncSession): Database session dependency injected by FastAPI.
        current_user (User): Current authenticated user injected by dependency.
        
    Returns:
        List[ContactResponse]: List of matching contact objects that belong to the user
                              and contain the search query in any searchable field.
        
    Raises:
        HTTPException: 401 if user is not authenticated.
        HTTPException: 422 if query parameter is missing or invalid.
        HTTPException: 500 if database error occurs during search.
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
    
    Retrieves all contacts belonging to the current user whose birthdays fall
    within the next 7 days from today. Useful for birthday reminder functionality.
    
    Args:
        skip (int, optional): Number of records to skip for pagination. Defaults to 0.
        limit (int, optional): Maximum number of records to return. Defaults to 100.
        db (AsyncSession): Database session dependency injected by FastAPI.
        current_user (User): Current authenticated user injected by dependency.
        
    Returns:
        List[ContactResponse]: List of contacts with birthdays in the next 7 days,
                              sorted by birthday date (earliest first).
        
    Raises:
        HTTPException: 401 if user is not authenticated.
        HTTPException: 500 if database error occurs during query.
        
    Note:
        The birthday calculation considers only the month and day, ignoring the year,
        so it works regardless of the birth year stored in the database.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_upcoming_birthdays(current_user.id, skip, limit)
    return contacts