from unittest.mock import patch, Mock
import pytest

from conftest import test_user


def test_get_me(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("api/users/me", headers=headers)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    assert "avatar" in data


@patch("src.services.users.cloudinary.uploader.upload")
@patch("src.services.users.cloudinary.utils.cloudinary_url")
@pytest.mark.asyncio
async def test_update_avatar_user(mock_cloudinary_url, mock_cloudinary_upload, client, get_admin_token):
    mock_upload_result = {
        'public_id': 'avatars/1',
        'version': '1234567890'
    }
    mock_cloudinary_upload.return_value = mock_upload_result
    
    fake_url = "http://example.com/avatar.jpg"
    mock_cloudinary_url.return_value = (fake_url, {})
    
    admin_token = await get_admin_token
    headers = {"Authorization": f"Bearer {admin_token}"}

    file_data = {"file": ("avatar.jpg", b"fake image content", "image/jpeg")}

    response = client.patch("/api/users/avatar", headers=headers, files=file_data)

    assert response.status_code == 200, response.text

    data = response.json()
    from conftest import test_admin_user
    assert data["username"] == test_admin_user["username"]
    assert data["email"] == test_admin_user["email"]
    assert data["avatar"] == fake_url

    mock_cloudinary_upload.assert_called_once()
    mock_cloudinary_url.assert_called_once()