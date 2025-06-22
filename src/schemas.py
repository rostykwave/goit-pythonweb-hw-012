from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import date
from typing import Optional
from src.database.models import UserRole

class ContactBase(BaseModel):
    """Base Pydantic model for Contact objects.
    
    Contains all shared attributes for Contact objects across the application.
    """
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    birth_date: date
    additional_data: Optional[str] = None

class ContactCreate(ContactBase):
    """Base Pydantic model for Contact objects.
    
    Contains all shared attributes for Contact objects across the application.
    """
    pass

class ContactUpdate(ContactBase):
    """Model for updating existing contacts.
    
    Inherits all fields from ContactBase without modifications.
    Used in PUT requests to /contacts/{contact_id} endpoint.
    """
    pass

class ContactResponse(ContactBase):
    """Model for contact responses.
    
    Extends the ContactBase model by adding the contact ID. 
    Used for returning contact data in API responses.
    """
    id: int
    
class Config:
    """Configuration class for ORM mode compatibility.
    
    Enables automatic conversion from SQLAlchemy models to Pydantic models.
    """
    from_attributes = True

class User(BaseModel):
    """Model representing a user in the system.
    
    Contains basic user profile information.
    Used for user-related responses in the API.
    """
    id: int
    username: str
    email: str
    avatar: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    """Model for creating new users.
    
    Contains required fields for user registration.
    Used in POST requests to /auth/signup endpoint.
    """
    username: str
    email: str
    password: str
    role: UserRole = UserRole.USER

class Token(BaseModel):
    """Authentication token model.
    
    Represents the JWT token response format after successful authentication.
    Used in responses from /auth/login endpoint.
    """
    access_token: str
    token_type: str

class RequestEmail(BaseModel):
    """Model for email-based requests.
    
    Used for endpoints that require only an email address,
    such as password reset or email verification requests.
    """
    email: EmailStr