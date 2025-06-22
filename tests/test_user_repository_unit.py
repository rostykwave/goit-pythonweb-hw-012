import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.repository.users import UserRepository
from src.schemas import UserCreate

@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session

@pytest.fixture
def user_repository(mock_session):
    return UserRepository(mock_session)

@pytest.fixture
def user():
    return User(id=1, username="testuser", email="test@example.com")

@pytest.mark.asyncio
async def test_get_user_by_id(user_repository, mock_session):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(
        id=1, username="test user", email="test@example.com"
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result_user = await user_repository.get_user_by_id(user_id=1)

    # Assertions
    assert result_user is not None
    assert result_user.id == 1
    assert result_user.username == "test user"

@pytest.mark.asyncio
async def test_get_user_by_username(user_repository, mock_session):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(
        id=1, username="testuser", email="test@example.com"
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result_user = await user_repository.get_user_by_username(username="testuser")

    # Assertions
    assert result_user is not None
    assert result_user.username == "testuser"

@pytest.mark.asyncio
async def test_get_user_by_email(user_repository, mock_session):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(
        id=1, username="testuser", email="test@example.com"
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result_user = await user_repository.get_user_by_email(email="test@example.com")

    # Assertions
    assert result_user is not None
    assert result_user.email == "test@example.com"

@pytest.mark.asyncio
async def test_create_user(user_repository, mock_session):
    # Setup
    user_data = UserCreate(
        username="new user",
        email="newuser@example.com",
        password="password123"
    )

    # Call method
    result = await user_repository.create_user(body=user_data, avatar="http://example.com/avatar.jpg")

    # Assertions
    assert isinstance(result, User)
    assert result.username == "new user"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)

@pytest.mark.asyncio
async def test_update_avatar(user_repository, mock_session):
    # Setup
    existing_user = User(id=1, username="testuser", email="test@example.com")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await user_repository.update_avatar(user_id=1, avatar_url="http://example.com/new_avatar.jpg")

    # Assertions
    assert result is not None
    assert result.avatar == "http://example.com/new_avatar.jpg"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_user)

@pytest.mark.asyncio
async def test_confirmed_email(user_repository, mock_session):
    # Setup
    existing_user = User(id=1, username="testuser", email="test@example.com", confirmed=False)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    await user_repository.confirmed_email(email="test@example.com")

    # Assertions
    assert existing_user.confirmed is True
    mock_session.commit.assert_awaited_once()