# users_service/test_app.py
# I run it by 'pytest --cov=app --maxfail=1 --disable-warnings -v'
import pytest
from flask import Flask
from app import app, users_db, save_users  # Import the app and necessary functions

@pytest.fixture
def client():
    """Setup Flask test client"""
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def reset_users_db():
    """Reset the users database before each test"""
    # Mock database reset before each test
    users_db.clear()
    save_users(users_db)
    yield
    # Reset DB after tests
    users_db.clear()
    save_users(users_db)

# Helper function to register a user
def register_user(client, name="John Doe", email="john@example.com", password="password123", role="User"):
    return client.post('/api/users/register', json={
        "name": name,
        "email": email,
        "password": password,
        "role": role
    })

# Helper function to login a user
def login_user(client, email="john@example.com", password="password123"):
    return client.post('/api/users/login', json={
        "email": email,
        "password": password
    })

# Test for user registration
def test_register_user(client):
    response = register_user(client)
    assert response.status_code == 201
    assert "Message" in response.json
    assert response.json["Message"] == "Registration successful as User"
    assert "User" in response.json
    assert response.json["User"]["email"] == "john@example.com"

# Test for email format validation during registration
def test_register_invalid_email(client):
    response = register_user(client, email="invalid-email")
    assert response.status_code == 400
    assert response.json["Message"] == "Invalid email format"

# Test for missing fields during registration
def test_register_missing_fields(client):
    response = client.post('/api/users/register', json={})
    assert response.status_code == 400
    assert response.json["Message"] == "Missing required fields"

# Test for conflicting email during registration
def test_register_existing_email(client):
    register_user(client)
    response = register_user(client, email="john@example.com")
    assert response.status_code == 409
    assert response.json["Message"] == "Email already registered"

# Test user login
def test_login_user(client):
    register_user(client)
    response = login_user(client)
    assert response.status_code == 200
    assert "accessToken" in response.json

# Test login with invalid credentials
def test_login_invalid_credentials(client):
    register_user(client)
    response = client.post('/api/users/login', json={
        "email": "john@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert response.json["Message"] == "Invalid credentials"

# Test getting user profile with a valid token
def test_profile_with_valid_token(client):
    register_user(client)
    login_response = login_user(client)
    access_token = login_response.json["accessToken"]
    response = client.post('/api/users/profile', json={"accessToken": access_token})
    assert response.status_code == 200
    assert response.json["Message"] == "Profile retrieved successfully"
    assert response.json["User"]["email"] == "john@example.com"

# Test getting user profile with an invalid token
def test_profile_invalid_token(client):
    response = client.post('/api/users/profile', json={"accessToken": "invalidtoken"})
    assert response.status_code == 401
    assert response.json["Message"] == "Invalid token"

# Test profile with expired token
def test_profile_expired_token(client, monkeypatch):
    register_user(client)
    # Create an expired token (use a mock or an old token for this test)
    expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # Create an expired token here
    response = client.post('/api/users/profile', json={"accessToken": expired_token})
    assert response.status_code == 401
    assert response.json["Message"] == "Token has expired"

# Test missing access token when fetching profile
def test_profile_missing_token(client):
    response = client.post('/api/users/profile', json={})
    assert response.status_code == 400
    assert response.json["Message"] == "Missing access token"

# Test profile for non-existent user
def test_profile_user_not_found(client):
    login_response = login_user(client)
    access_token = login_response.json["accessToken"]
    response = client.post('/api/users/profile', json={"accessToken": access_token})
    assert response.status_code == 404
    assert response.json["Message"] == "User not found"
