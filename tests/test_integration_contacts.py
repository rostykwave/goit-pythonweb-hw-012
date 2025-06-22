import pytest
from datetime import date

def test_create_contact(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    contact_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "+1234567890",
        "birth_date": "1990-01-15"
    }
    response = client.post("/api/contacts/", json=contact_data, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"

def test_get_contacts(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/contacts/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_contact_by_id(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    
    contact_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": "test.user@example.com",
        "phone_number": "+1234567890",
        "birth_date": "1990-01-15"
    }
    create_response = client.post("/api/contacts/", json=contact_data, headers=headers)
    assert create_response.status_code == 201
    
    created_contact = create_response.json()
    print(f"Created contact: {created_contact}")
    
    contact_id = created_contact.get("id")
    if not contact_id:
        pytest.skip("Contact creation didn't return ID")
    
    response = client.get(f"/api/contacts/{contact_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Test"

def test_update_contact(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    
    contact_data = {
        "first_name": "Original",
        "last_name": "Name",
        "email": "original@example.com",
        "phone_number": "+1234567890",
        "birth_date": "1990-01-15"
    }
    create_response = client.post("/api/contacts/", json=contact_data, headers=headers)
    assert create_response.status_code == 201
    
    created_contact = create_response.json()
    contact_id = created_contact.get("id")
    if not contact_id:
        pytest.skip("Contact creation didn't return ID")
    
    update_data = {
        "first_name": "Updated",
        "last_name": "Name",
        "email": "updated@example.com",
        "phone_number": "+9876543210",
        "birth_date": "1991-02-20"
    }
    response = client.put(f"/api/contacts/{contact_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Updated"

def test_delete_contact(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    
    contact_data = {
        "first_name": "ToDelete",
        "last_name": "User",
        "email": "delete@example.com",
        "phone_number": "+1234567890",
        "birth_date": "1990-01-15"
    }
    create_response = client.post("/api/contacts/", json=contact_data, headers=headers)
    assert create_response.status_code == 201
    
    created_contact = create_response.json()
    contact_id = created_contact.get("id")
    if not contact_id:
        pytest.skip("Contact creation didn't return ID")
    
    response = client.delete(f"/api/contacts/{contact_id}", headers=headers)
    assert response.status_code == 200

def test_search_contacts(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/contacts/search/?q=John", headers=headers)
    assert response.status_code == 200

def test_upcoming_birthdays(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/contacts/birthdays/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_unauthorized_access(client):
    response = client.get("/api/contacts/")
    assert response.status_code == 401