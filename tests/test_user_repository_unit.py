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

@pytest.mark.asyncio
async def test_update_user_password(user_repository, mock_session):
    # Setup
    existing_user = User(id=1, username="testuser", email="test@example.com", hashed_password="old_password")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await user_repository.update_user_password(email="test@example.com", new_password="new_password")

    # Assertions
    assert result is not None
    assert result.email == "test@example.com"
    mock_session.execute.assert_called()
    mock_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_all_users(user_repository, mock_session):
    # Setup
    users = [
        User(id=1, username="user1", email="user1@example.com"),
        User(id=2, username="user2", email="user2@example.com")
    ]
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = users
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await user_repository.get_all_users(skip=0, limit=10)

    # Assertions
    assert len(result) == 2
    assert result[0].username == "user1"
    assert result[1].username == "user2"
    mock_session.execute.assert_called_once()

@pytest.mark.asyncio
async def test_update_user_role(user_repository, mock_session):
    # Setup
    from src.database.models import UserRole
    existing_user = User(id=1, username="testuser", email="test@example.com", role=UserRole.USER)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await user_repository.update_user_role(user_id=1, role=UserRole.ADMIN)

    # Assertions
    assert result is not None
    assert result.id == 1
    mock_session.execute.assert_called()
    mock_session.commit.assert_awaited_once()

@pytest.mark.asyncio
async def test_update_avatar_user_not_found(user_repository, mock_session):
    # Setup
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Call method
    result = await user_repository.update_avatar(user_id=999, avatar_url="http://example.com/avatar.jpg")

    # Assertions
    assert result is None
    mock_session.commit.assert_not_awaited()
    mock_session.refresh.assert_not_awaited()