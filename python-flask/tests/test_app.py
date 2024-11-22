# tests/test_app.py
import pytest
import json
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app, JWT_SECRET
from routes.users import users_db, save_users, load_users
from routes.destinations import destinations_db, save_destinations, load_destinations

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_users():
    users_db.clear()
    test_users = {
        "1": {
            "id": 1,
            "name": "Test Admin",
            "email": "admin@test.com",
            "password": generate_password_hash("admin123"),
            "type": "Admin"
        },
        "2": {
            "id": 2,
            "name": "Test User",
            "email": "user@test.com",
            "password": generate_password_hash("user123"),
            "type": "User"
        }
    }
    users_db.update(test_users)
    save_users(users_db)
    return test_users

@pytest.fixture
def mock_destinations():
    destinations_db.clear()
    test_destinations = {
        "1": {
            "id": 1,
            "name": "Test Destination",
            "description": "Test Description",
            "location": "Test Location"
        }
    }
    destinations_db.update(test_destinations)
    save_destinations(destinations_db)
    return test_destinations

@pytest.fixture
def admin_token():
    payload = {
        "id": 1,
        "email": "admin@test.com",
        "type": "Admin",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

@pytest.fixture
def user_token():
    payload = {
        "id": 2,
        "email": "user@test.com",
        "type": "User",
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

# User Registration Tests
class TestUserRegistration:
    def test_successful_registration(self, client):
        response = client.post('/api/users/register', json={
            "name": "New User",
            "email": "new@test.com",
            "password": "password123",
            "role": "User"
        })
        assert response.status_code == 201
        assert "User" in response.json
        assert response.json["User"]["email"] == "new@test.com"

    def test_invalid_email_format(self, client):
        response = client.post('/api/users/register', json={
            "name": "Invalid",
            "email": "invalid-email",
            "password": "password123",
            "role": "User"
        })
        assert response.status_code == 400
        assert "Invalid email format" in response.json["Message"]

    def test_duplicate_email(self, client, mock_users):
        response = client.post('/api/users/register', json={
            "name": "Duplicate",
            "email": "admin@test.com",
            "password": "password123",
            "role": "User"
        })
        assert response.status_code == 409
        assert "Email already registered" in response.json["Message"]

    def test_invalid_role(self, client):
        response = client.post('/api/users/register', json={
            "name": "Invalid Role",
            "email": "invalid@test.com",
            "password": "password123",
            "role": "InvalidRole"
        })
        assert response.status_code == 400
        assert "Invalid role" in response.json["Message"]

# User Login Tests
class TestUserLogin:
    def test_successful_login(self, client, mock_users):
        response = client.post('/api/users/login', json={
            "email": "admin@test.com",
            "password": "admin123"
        })
        assert response.status_code == 200
        assert "accessToken" in response.json

    def test_invalid_credentials(self, client, mock_users):
        response = client.post('/api/users/login', json={
            "email": "admin@test.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401
        assert "Invalid credentials" in response.json["Message"]

# User Profile Tests
class TestUserProfile:
    def test_view_profile_success(self, client, mock_users, admin_token):
        response = client.get(f'/api/users/profile?accessToken={admin_token}')
        assert response.status_code == 200
        assert response.json["email"] == "admin@test.com"

    def test_view_profile_invalid_token(self, client):
        response = client.get('/api/users/profile?accessToken=invalid_token')
        assert response.status_code == 401
        assert "Invalid token" in response.json["Message"]

    def test_view_profile_missing_token(self, client):
        response = client.get('/api/users/profile')
        assert response.status_code == 401
        assert "token missing" in response.json["Message"]

# Destination Management Tests
class TestDestinations:
    def test_get_all_destinations(self, client, mock_destinations):
        response = client.get('/api/destinations/all_destinations')
        assert response.status_code == 200
        assert len(response.json) > 0

    def test_create_destination_admin(self, client, admin_token):
        response = client.post(
            f'/api/destinations/create_destination?accessToken={admin_token}',
            json={
                "name": "New Destination",
                "description": "New Description",
                "location": "New Location"
            }
        )
        assert response.status_code == 201
        assert response.json["Message"] == "Destination created successfully."

    def test_create_destination_unauthorized(self, client, user_token):
        response = client.post(
            f'/api/destinations/create_destination?accessToken={user_token}',
            json={
                "name": "New Destination",
                "description": "New Description",
                "location": "New Location"
            }
        )
        assert response.status_code == 403
        assert "Only Admins are authorized" in response.json["Message"]

    def test_delete_destination_admin(self, client, mock_destinations, admin_token):
        response = client.delete(f'/api/destinations/1?accessToken={admin_token}')
        assert response.status_code == 200
        assert "Destination deleted" in response.json["Message"]

    def test_delete_destination_unauthorized(self, client, mock_destinations, user_token):
        response = client.delete(f'/api/destinations/1?accessToken={user_token}')
        assert response.status_code == 403
        assert "Only Admins are authorized" in response.json["Message"]

    def test_delete_nonexistent_destination(self, client, admin_token):
        response = client.delete(f'/api/destinations/999?accessToken={admin_token}')
        assert response.status_code == 404
        assert "Destination not found" in response.json["Message"]

# Authentication Tests
class TestAuthentication:
    def test_missing_token(self, client):
        response = client.delete('/api/destinations/1')
        assert response.status_code == 403
        assert "token missing" in response.json["Message"]

    def test_expired_token(self, client):
        payload = {
            "id": 1,
            "email": "admin@test.com",
            "type": "Admin",
            "exp": datetime.utcnow() - timedelta(hours=1)
        }
        expired_token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        response = client.delete(f'/api/destinations/1?accessToken={expired_token}')
        assert response.status_code == 403
        assert "Token expired" in response.json["Message"]

# Input Validation Tests
class TestInputValidation:
    def test_missing_required_fields_registration(self, client):
        response = client.post('/api/users/register', json={
            "name": "Test User"
        })
        assert response.status_code == 400

    def test_missing_required_fields_destination(self, client, admin_token):
        response = client.post(
            f'/api/destinations/create_destination?accessToken={admin_token}',
            json={
                "name": "Test Destination"
            }
        )
        assert response.status_code == 400
        assert "required" in response.json["Message"]

# File Operations Tests
class TestFileOperations:
    def test_load_users(self, mock_users):
        loaded_users = load_users()
        assert loaded_users == users_db
        assert "1" in loaded_users

    def test_load_destinations(self, mock_destinations):
        loaded_destinations = load_destinations()
        assert loaded_destinations == destinations_db
        assert "1" in loaded_destinations

    def test_save_users(self, mock_users):
        new_user = {
            "id": 3,
            "name": "Test Save",
            "email": "save@test.com",
            "password": generate_password_hash("save123"),
            "type": "User"
        }
        users_db["3"] = new_user
        save_users(users_db)
        loaded_users = load_users()
        assert "3" in loaded_users
        assert loaded_users["3"]["email"] == "save@test.com"

if __name__ == '__main__':
    pytest.main(['-v', '--cov=app', '--cov-report=term-missing'])