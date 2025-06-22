from sqlalchemy import String, Date, Text, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from datetime import date
from typing import Optional
from enum import Enum

class Base(DeclarativeBase):
    pass

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class User(Base):
    """
    User model for authentication and contact ownership.
    
    Attributes:
        id (int): Primary key
        username (str): Unique username for login
        email (str): User's email address
        hashed_password (str): Bcrypt hashed password
        confirmed (bool): Email confirmation status
        avatar (str, optional): URL to user avatar image
        role (UserRole): User role (USER or ADMIN)
        contacts (List[Contact]): List of user's contacts
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.USER)
    
    contacts: Mapped[list["Contact"]] = relationship("Contact", back_populates="owner")

class Contact(Base):
    """
    Contact model for storing contact information.
    
    Attributes:
        id (int): Primary key
        first_name (str): Contact's first name
        last_name (str): Contact's last name
        email (str): Contact's email address
        phone_number (str): Contact's phone number
        birth_date (date): Contact's birth date
        additional_data (str, optional): Additional notes about contact
        user_id (int): Foreign key to User model
        owner (User): User who owns this contact
    """
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(50), index=True)
    last_name: Mapped[str] = mapped_column(String(50), index=True)
    email: Mapped[str] = mapped_column(String(100), index=True)
    phone_number: Mapped[str] = mapped_column(String(20))
    birth_date: Mapped[date] = mapped_column(Date)
    additional_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    
    owner: Mapped["User"] = relationship("User", back_populates="contacts")