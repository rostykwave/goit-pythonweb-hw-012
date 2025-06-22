import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.schemas import ContactCreate, ContactUpdate

@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session

@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)

@pytest.fixture
def test_user():
    return User(id=1, username="testuser", email="test@example.com")

@pytest.fixture
def test_contact():
    return Contact(
        id=1,
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="+1234567890",
        birth_date=date(1990, 1, 15),
        user_id=1
    )

@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session):
    # Setup
    contacts = [
        Contact(id=1, first_name="John", last_name="Doe", user_id=1),
        Contact(id=2, first_name="Jane", last_name="Smith", user_id=1)
    ]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = contacts
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.get_contacts(skip=0, limit=10, user_id=1)

    # Assertions
    assert len(result) == 2
    assert result[0].first_name == "John"
    assert result[1].first_name == "Jane"

@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, test_contact):
    # Setup
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = test_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.get_contact_by_id(contact_id=1)

    # Assertions
    assert result is not None
    assert result.id == 1
    assert result.first_name == "John"

@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session):
    # Setup
    contact_data = ContactCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone_number="+1234567890",
        birth_date=date(1990, 1, 15)
    )

    # Call method
    result = await contact_repository.create_contact(body=contact_data, user_id=1)

    # Assertions
    assert isinstance(result, Contact)
    assert result.first_name == "John"
    assert result.user_id == 1
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()

@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, test_contact):
    # Setup
    contact_repository.get_contact_by_id = AsyncMock(return_value=test_contact)
    
    update_data = ContactUpdate(
        first_name="Updated John",
        last_name="Updated Doe",
        email="updated@example.com",
        phone_number="+9876543210",
        birth_date=date(1991, 2, 20)
    )

    # Call method
    result = await contact_repository.update_contact(contact_id=1, body=update_data)

    # Assertions
    assert result is not None
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()

@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, test_contact):
    # Setup
    contact_repository.get_contact_by_id = AsyncMock(return_value=test_contact)

    # Call method
    result = await contact_repository.remove_contact(contact_id=1)

    # Assertions
    assert result is not None
    mock_session.delete.assert_called_once_with(test_contact)
    mock_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_search_contacts(contact_repository, mock_session):
    # Setup
    contacts = [Contact(id=1, first_name="John", last_name="Doe", user_id=1)]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = contacts
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.search_contacts(query="John", user_id=1)

    # Assertions
    assert len(result) == 1
    assert result[0].first_name == "John"

@pytest.mark.asyncio
async def test_get_upcoming_birthdays(contact_repository, mock_session):
    # Setup
    contacts = [Contact(id=1, first_name="John", birth_date=date.today(), user_id=1)]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = contacts
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await contact_repository.get_upcoming_birthdays(user_id=1, skip=0, limit=10)

    # Assertions
    assert len(result) == 1
    assert result[0].first_name == "John"