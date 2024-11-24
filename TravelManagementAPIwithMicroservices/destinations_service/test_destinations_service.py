# destinations_service/test_destinations_service.py


import pytest
import json
from app import app, destinations_db, load_destinations, save_destinations, JWT_SECRET
import jwt
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock, mock_open
import os

# Test fixtures
@pytest.fixture
def client():
    """Test client fixture"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def mock_destinations_db():
    """Mock destinations database fixture"""
    mock_db = {
        "1": {
            "id": 1,
            "name": "Paris",
            "description": "Capital of France",
            "location": "Europe"
        },
        "2": {
            "id": 2,
            "name": "Tokyo",
            "description": "Capital of Japan",
            "location": "Asia"
        }
    }
    with patch.dict('app.destinations_db', mock_db, clear=True):
        yield mock_db

@pytest.fixture
def mock_file_operations():
    """Mock file operations fixture"""
    mock_data = {}
    
    def mock_save(data):
        nonlocal mock_data
        mock_data = data
    
    def mock_load():
        return mock_data
    
    with patch('app.save_destinations', side_effect=mock_save), \
         patch('app.load_destinations', side_effect=mock_load), \
         patch('builtins.open', mock_open()):
        yield mock_data

def generate_token(user_id, user_type="User", expired=False, missing_type=False):
    """Helper function to generate JWT tokens"""
    payload = {
        "id": user_id,
        "email": f"test{user_id}@example.com",
        "exp": datetime.utcnow() + timedelta(hours=-1 if expired else 3)
    }
    if not missing_type:
        payload["type"] = user_type
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

class TestDestinationsService:
    """Test class for Destinations Service"""

    # Token Verification Tests
    def test_verify_token_success(self, client):
        """Test successful token verification"""
        token = generate_token(1, "User")
        response = client.get(
            '/api/destinations/all',
            headers={"accessToken": token}
        )
        assert response.status_code == 200

    def test_verify_token_expired(self, client):
        """Test expired token handling"""
        token = generate_token(1, "User", expired=True)
        response = client.get(
            '/api/destinations/all',
            headers={"accessToken": token}
        )
        assert response.status_code == 403
        assert "Invalid token" in response.get_json()["Message"]

    def test_verify_token_missing(self, client):
        """Test missing token handling"""
        response = client.get('/api/destinations/all')
        assert response.status_code == 403
        assert "Unauthorized, token missing" in response.get_json()["Message"]

    def test_verify_token_invalid_format(self, client):
        """Test invalid token format handling"""
        response = client.get(
            '/api/destinations/all',
            headers={"accessToken": "invalid.token.format"}
        )
        assert response.status_code == 403
        assert "Invalid token" in response.get_json()["Message"]

    # Create Destination Tests
    def test_create_destination_success(self, client, mock_file_operations):
        """Test successful destination creation"""
        token = generate_token(1, "Admin")
        data = {
            "name": "New York",
            "description": "The Big Apple",
            "location": "North America"
        }
        
        response = client.post(
            '/api/destinations/create',
            headers={"Authorization": f"Bearer {token}"},
            json=data
        )
        
        assert response.status_code == 201
        result = response.get_json()
        assert result["name"] == "New York"
        assert "id" in result
        assert result["description"] == "The Big Apple"
        assert result["location"] == "North America"

    def test_create_destination_non_admin(self, client):
        """Test creation attempt by non-admin user"""
        token = generate_token(1, "User")
        data = {
            "name": "London",
            "description": "Capital of UK",
            "location": "Europe"
        }
        
        response = client.post(
            '/api/destinations/create',
            headers={"Authorization": f"Bearer {token}"},
            json=data
        )
        
        assert response.status_code == 403
        assert "Access Denied: Admin only" in response.get_json()["Message"]

    def test_create_destination_missing_fields(self, client):
        """Test creation with missing required fields"""
        token = generate_token(1, "Admin")
        incomplete_data = {
            "name": "Berlin"
            # missing description and location
        }
        
        response = client.post(
            '/api/destinations/create',
            headers={"Authorization": f"Bearer {token}"},
            json=incomplete_data
        )
        
        assert response.status_code == 400
        assert "Missing required fields" in response.get_json()["Message"]

    # Get Destinations Tests
    def test_get_all_destinations(self, client, mock_destinations_db):
        """Test getting all destinations"""
        token = generate_token(1, "User")
        response = client.get(
            '/api/destinations/all',
            headers={"accessToken": token}
        )
        
        assert response.status_code == 200
        result = response.get_json()
        assert isinstance(result, list)
        assert len(result) == 2
        assert any(d["name"] == "Paris" for d in result)
        assert any(d["name"] == "Tokyo" for d in result)

    def test_get_destination_by_id(self, client, mock_destinations_db):
        """Test getting specific destination by ID"""
        token = generate_token(1, "User")
        response = client.get(
            '/api/destinations/1',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        result = response.get_json()
        assert result["name"] == "Paris"
        assert result["description"] == "Capital of France"

    def test_get_destination_not_found(self, client, mock_destinations_db):
        """Test getting non-existent destination"""
        token = generate_token(1, "User")
        response = client.get(
            '/api/destinations/999',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 404
        assert "Destination not found" in response.get_json()["Message"]

    # Delete Destination Tests
    def test_delete_destination_success(self, client, mock_destinations_db, mock_file_operations):
        """Test successful destination deletion"""
        token = generate_token(1, "Admin")
        response = client.delete(
            '/api/destinations/1',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        assert "Destination deleted" in response.get_json()["Message"]
        assert "1" not in destinations_db

    def test_delete_destination_non_admin(self, client, mock_destinations_db):
        """Test deletion attempt by non-admin user"""
        token = generate_token(1, "User")
        response = client.delete(
            '/api/destinations/1',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
        assert "Access Denied: Admin only" in response.get_json()["Message"]

    # File Operations Tests
    def test_load_destinations_file_not_exists(self):
        """Test loading destinations when file doesn't exist"""
        with patch('os.path.exists', return_value=False):
            result = load_destinations()
            assert result == {}

    def test_load_destinations_corrupted_file(self):
        """Test loading corrupted destinations file"""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data="invalid json")):
            result = load_destinations()
            assert result == {}

    def test_save_destinations_error(self):
        """Test handling of save operation errors"""
        with patch('builtins.open') as mock_file:
            mock_file.side_effect = IOError("Failed to write file")
            with pytest.raises(IOError):
                save_destinations({"test": "data"})

    # Authorization Header Tests
    def test_authorization_header_variations(self, client, mock_file_operations):
        """Test different authorization header formats"""
        token = generate_token(1, "Admin")
        data = {
            "name": "Test",
            "description": "Test Desc",
            "location": "Test Loc"
        }
        
        # Test with lowercase 'bearer'
        response = client.post(
            '/api/destinations/create',
            headers={"Authorization": f"bearer {token}"},
            json=data
        )
        assert response.status_code == 201
        
        # Test with extra whitespace
        response = client.post(
            '/api/destinations/create',
            headers={"Authorization": f"Bearer  {token}  "},
            json=data
        )
        assert response.status_code == 201

    # Concurrent Operations Tests
    def test_concurrent_operations(self, client, mock_file_operations):
        """Test handling of concurrent operations"""
        token = generate_token(1, "Admin")
        
        # Create multiple destinations
        created_ids = set()
        for i in range(5):
            response = client.post(
                '/api/destinations/create',
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "name": f"Test {i}",
                    "description": f"Test Description {i}",
                    "location": f"Test Location {i}"
                }
            )
            assert response.status_code == 201
            created_ids.add(response.get_json()["id"])
        
        # Verify all IDs are unique
        assert len(created_ids) == 5

    # API Documentation Test
    def test_api_documentation(self, client):
        """Test API documentation endpoint"""
        response = client.get('/swagger.json')
        assert response.status_code == 200
        swagger_doc = response.get_json()
        
        # Verify essential documentation elements
        assert 'paths' in swagger_doc
        assert '/api/destinations/all' in swagger_doc['paths']
        assert '/api/destinations/create' in swagger_doc['paths']

if __name__ == '__main__':
    pytest.main(['-v'])






# # import pytest
# # import json
# # from app import app
# # import jwt
# # from datetime import datetime, timedelta
# # from unittest.mock import patch, MagicMock

# # # Test setup for testing client
# # @pytest.fixture
# # def client():
# #     app.config['TESTING'] = True
# #     app.config['JWT_SECRET'] = "test_secret_key"
# #     with app.test_client() as client:
# #         yield client

# # # Mocked function to avoid file system dependence
# # @pytest.fixture
# # def mock_load_destinations():
# #     with patch("app.load_destinations", return_value={}):
# #         yield

# # @pytest.fixture
# # def mock_save_destinations():
# #     with patch("app.save_destinations") as mock:
# #         yield mock

# # @pytest.fixture
# # def mock_delete_destination():
# #     with patch("app.delete_destination") as mock:
# #         yield mock

# # @pytest.fixture
# # def mock_find_destination_by_id():
# #     with patch("app.find_destination_by_id") as mock:
# #         yield mock

# # # Create a function to generate a JWT token for a mock user

# # def generate_token(user_id, user_type="User"):
# #     payload = {
# #         "id": user_id,
# #         "email": f"test{user_id}@example.com",
# #         "type": user_type,
# #         "exp": datetime.utcnow() + timedelta(hours=3)
# #     }
    
# #     token = jwt.encode(payload, app.config['JWT_SECRET'], algorithm="HS256")
# #     print(f"Generated Token: {token}")  # Debugging line to verify the token
# #     return token

# # # --- Test Destinations Service routes ---
# # class TestDestinationsService:

# #     # Test creating destination (Admin only)
# #     def test_create_destination(self, client, mock_save_destinations):
# #         token = generate_token(1, "Admin")  # Admin token
# #         print(f"Using Token: {token}")  # Debugging line to verify token being sent
# #         data = {
# #             "name": "Paris",
# #             "description": "Capital of France",
# #             "location": "Europe"
# #         }

# #         response = client.post('/api/destinations/create',
# #                             headers={"Authorization": f"Bearer {token}"},
# #                             json=data)

# #         print(f"Response status: {response.status_code}")  # Check status code
# #         print(f"Response data: {response.get_json()}")  # Check response content
        
# #         assert response.status_code == 201

    
# #         json_data = response.get_json()
# #         assert "id" in json_data
# #         assert json_data["name"] == "Paris"
# #         mock_save_destinations.assert_called_once()

# #     # Test creating destination as User (should fail)
# #     def test_create_destination_as_user(self, client):
# #         token = generate_token(2, "User")  # User token

# #         data = {
# #             "name": "London",
# #             "description": "Capital of England",
# #             "location": "Europe"
# #         }

# #         response = client.post('/api/destinations/create', 
# #                                headers={"Authorization": f"Bearer {token}"},
# #                                json=data)

# #         assert response.status_code == 403
# #         json_data = response.get_json()
# #         assert json_data["Message"] == "Access Denied: Admin only"

# #     # Test retrieving all destinations
# #     def test_get_destinations(self, client, mock_load_destinations):
# #         token = generate_token(1, "Admin")  # Admin token
# #         response = client.get('/api/destinations/all', 
# #                               headers={"Authorization": f"Bearer {token}"})

# #         assert response.status_code == 200
# #         json_data = response.get_json()
# #         assert isinstance(json_data, list)

# #     # Test retrieving a specific destination by ID
# #     def test_get_destination_by_id(self, client, mock_load_destinations, mock_find_destination_by_id):
# #         token = generate_token(1, "Admin")  # Admin token

# #         data = {
# #             "name": "Rome",
# #             "description": "Capital of Italy",
# #             "location": "Europe"
# #         }

# #         create_response = client.post('/api/destinations/create', 
# #                                       headers={"Authorization": f"Bearer {token}"},
# #                                       json=data)
# #         destination_id = create_response.get_json()["id"]

# #         # Now retrieve it by ID
# #         response = client.get(f'/api/destinations/{destination_id}', 
# #                               headers={"Authorization": f"Bearer {token}"})
        
# #         assert response.status_code == 200
# #         json_data = response.get_json()
# #         assert json_data["id"] == destination_id
# #         assert json_data["name"] == "Rome"

# #     # Test destination not found (404)
# #     def test_get_destination_not_found(self, client, mock_load_destinations, mock_find_destination_by_id):
# #         token = generate_token(1, "Admin")  # Admin token
# #         mock_find_destination_by_id.return_value = None  # Simulate no destination found

# #         response = client.get('/api/destinations/99999', 
# #                               headers={"Authorization": f"Bearer {token}"})

# #         assert response.status_code == 404
# #         json_data = response.get_json()
# #         assert json_data["Message"] == "Destination not found"

# #     # Test deleting destination (Admin only)
# #     def test_delete_destination(self, client, mock_delete_destination, mock_load_destinations):
# #         token = generate_token(1, "Admin")  # Admin token

# #         data = {
# #             "name": "Berlin",
# #             "description": "Capital of Germany",
# #             "location": "Europe"
# #         }

# #         create_response = client.post('/api/destinations/create', 
# #                                       headers={"Authorization": f"Bearer {token}"},
# #                                       json=data)
# #         destination_id = create_response.get_json()["id"]

# #         delete_response = client.delete(f'/api/destinations/{destination_id}', 
# #                                         headers={"Authorization": f"Bearer {token}"})


# #         assert delete_response.status_code == 200
# #         json_data = delete_response.get_json()
# #         assert json_data["Message"].startswith("Destination deleted")
# #         mock_delete_destination.assert_called_once()

# #     # Test deleting destination as User (should fail)
# #     def test_delete_destination_as_user(self, client):
# #         token = generate_token(2, "User")  # User token

# #         data = {
# #             "name": "Tokyo",
# #             "description": "Capital of Japan",
# #             "location": "Asia"
# #         }

# #         create_response = client.post('/api/destinations/create', 
# #                                       headers={"Authorization": f"Bearer {token}"},
# #                                       json=data)
# #         destination_id = create_response.get_json()["id"]

# #         delete_response = client.delete(f'/api/destinations/{destination_id}', 
# #                                         headers={"Authorization": f"Bearer {token}"})

# #         assert delete_response.status_code == 403
# #         json_data = delete_response.get_json()
# #         assert json_data["Message"] == "Access Denied: Admin only"

# #     # Test unauthorized access (no token)
# #     def test_unauthorized_access(self, client):
# #         response = client.get('/api/destinations/all')
# #         assert response.status_code == 401
# #         json_data = response.get_json()
# #         assert json_data["Message"] == "Unauthorized, token missing"

# #     # Test invalid token (JWT)
# #     def test_invalid_token(self, client):
# #         response = client.get('/api/destinations/all', 
# #                               headers={"Authorization": "Bearer invalid_token"})
# #         assert response.status_code == 401
# #         json_data = response.get_json()
# #         assert json_data["Message"] == "Invalid token"

# #     # Test expired token (JWT)
# #     def test_expired_token(self, client):
# #         expired_token = jwt.encode({
# #             "id": 1,
# #             "email": "test@example.com",
# #             "type": "Admin",
# #             "exp": datetime.utcnow() - timedelta(seconds=1)  # Expired token
# #         }, app.config['JWT_SECRET'], algorithm="HS256")

# #         response = client.get('/api/destinations/all', 
# #                               headers={"Authorization": f"Bearer {expired_token}"})
# #         assert response.status_code == 401
# #         json_data = response.get_json()
# #         assert json_data["Message"] == "Token has expired"

# #     # Test missing fields when creating destination
# #     def test_create_destination_missing_fields(self, client):
# #         token = generate_token(1, "Admin")

# #         data = {
# #             "name": "Sydney",
# #             "location": "Australia"  # Missing description
# #         }

# #         response = client.post('/api/destinations/create', 
# #                                headers={"Authorization": f"Bearer {token}"},
# #                                json=data)

# #         assert response.status_code == 400
# #         json_data = response.get_json()
# #         assert json_data["Message"] == "Missing required fields"

# #     # Test invalid data types when creating destination
# #     def test_create_destination_invalid_data(self, client):
# #         token = generate_token(1, "Admin")

# #         data = {
# #             "name": "Sydney",
# #             "description": 12345,  # Invalid type
# #             "location": "Australia"
# #         }

# #         response = client.post('/api/destinations/create', 
# #                                headers={"Authorization": f"Bearer {token}"},
# #                                json=data)

# #         assert response.status_code == 400
# #         json_data = response.get_json()
# #         assert json_data["Message"] == "Invalid data format"

# #     # Test deleting a non-existing destination (should fail)
# #     def test_delete_non_existing_destination(self, client, mock_delete_destination):
# #         token = generate_token(1, "Admin")

# #         response = client.delete('/api/destinations/99999', 
# #                                  headers={"Authorization": f"Bearer {token}"})

# #         assert response.status_code == 404
# #         json_data = response.get_json()
# #         assert json_data["Message"] == "Destination not found"

# #     # Test server error simulation (500)
# #     def test_server_error(self, client):
# #         with patch("app.save_destinations", side_effect=Exception("Database failure")):
# #             token = generate_token(1, "Admin")
# #             data = {
# #                 "name": "New York",
# #                 "description": "City in USA",
# #                 "location": "America"
# #             }

# #             response = client.post('/api/destinations/create', 
# #                                    headers={"Authorization": f"Bearer {token}"},
# #                                    json=data)

# #             assert response.status_code == 500
# #             json_data = response.get_json()
# #             assert json_data["Message"] == "Internal server error"

# #     # Test that an empty destinations list returns the correct response
# #     def test_get_empty_destinations(self, client):
# #         token = generate_token(1, "Admin")
# #         response = client.get('/api/destinations/all', 
# #                               headers={"Authorization": f"Bearer {token}"})
# #         assert response.status_code == 200
# #         json_data = response.get_json()
# #         assert json_data == []


# import pytest
# import json
# from app import app
# import jwt
# from datetime import datetime, timedelta
# from unittest.mock import patch, MagicMock

# # Test setup for testing client
# @pytest.fixture
# def client():
#     app.config['TESTING'] = True
#     app.config['JWT_SECRET'] = "test_secret_key"
#     with app.test_client() as client:
#         yield client

# # Mocked function to avoid file system dependence
# @pytest.fixture
# def mock_load_destinations():
#     with patch("app.load_destinations", return_value={}):
#         yield

# @pytest.fixture
# def mock_save_destinations():
#     with patch("app.save_destinations") as mock:
#         yield mock

# @pytest.fixture
# def mock_delete_destination():
#     with patch("app.delete_destination") as mock:
#         yield mock

# @pytest.fixture
# def mock_find_destination_by_id():
#     with patch("app.find_destination_by_id") as mock:
#         yield mock

# # Create a function to generate a JWT token for a mock user
# def generate_token(user_id, user_type="User"):
#     payload = {
#         "id": user_id,
#         "email": f"test{user_id}@example.com",
#         "type": user_type,
#         "exp": datetime.utcnow() + timedelta(hours=3)
#     }
#     token = jwt.encode(payload, app.config['JWT_SECRET'], algorithm="HS256")
#     return token

# # --- Test Destinations Service routes ---
# class TestDestinationsService:

#     # Test creating destination (Admin only)
#     def test_create_destination(self, client, mock_save_destinations):
#         token = generate_token(1, "Admin")  # Admin token
#         data = {
#             "name": "Paris",
#             "description": "Capital of France",
#             "location": "Europe"
#         }

#         response = client.post('/api/destinations/create',
#                             headers={"Authorization": f"Bearer {token}"},
#                             json=data)
        
#         assert response.status_code == 201
#         json_data = response.get_json()
#         assert "id" in json_data
#         assert json_data["name"] == "Paris"
#         mock_save_destinations.assert_called_once()

#     # Test creating destination as User (should fail)
#     def test_create_destination_as_user(self, client):
#         token = generate_token(2, "User")  # User token

#         data = {
#             "name": "London",
#             "description": "Capital of England",
#             "location": "Europe"
#         }

#         response = client.post('/api/destinations/create', 
#                                headers={"Authorization": f"Bearer {token}"},
#                                json=data)

#         assert response.status_code == 403
#         json_data = response.get_json()
#         assert json_data["Message"] == "Access Denied: Admin only"

#     # Test retrieving all destinations
#     def test_get_destinations(self, client, mock_load_destinations):
#         token = generate_token(1, "Admin")  # Admin token
#         response = client.get('/api/destinations/all', 
#                               headers={"Authorization": f"Bearer {token}"})

#         assert response.status_code == 200
#         json_data = response.get_json()
#         assert isinstance(json_data, list)

#     # Test retrieving a specific destination by ID
#     def test_get_destination_by_id(self, client, mock_load_destinations, mock_find_destination_by_id):
#         token = generate_token(1, "Admin")  # Admin token

#         data = {
#             "name": "Rome",
#             "description": "Capital of Italy",
#             "location": "Europe"
#         }

#         create_response = client.post('/api/destinations/create', 
#                                       headers={"Authorization": f"Bearer {token}"},
#                                       json=data)
#         destination_id = create_response.get_json()["id"]

#         # Now retrieve it by ID
#         response = client.get(f'/api/destinations/{destination_id}', 
#                               headers={"Authorization": f"Bearer {token}"})
        
#         assert response.status_code == 200
#         json_data = response.get_json()
#         assert json_data["id"] == destination_id
#         assert json_data["name"] == "Rome"

#     # Test destination not found (404)
#     def test_get_destination_not_found(self, client, mock_load_destinations, mock_find_destination_by_id):
#         token = generate_token(1, "Admin")  # Admin token
#         mock_find_destination_by_id.return_value = None  # Simulate no destination found

#         response = client.get('/api/destinations/99999', 
#                               headers={"Authorization": f"Bearer {token}"})

#         assert response.status_code == 404
#         json_data = response.get_json()
#         assert json_data["Message"] == "Destination not found"

#     # Test deleting destination (Admin only)
#     def test_delete_destination(self, client, mock_delete_destination, mock_load_destinations):
#         token = generate_token(1, "Admin")  # Admin token

#         data = {
#             "name": "Berlin",
#             "description": "Capital of Germany",
#             "location": "Europe"
#         }

#         create_response = client.post('/api/destinations/create', 
#                                       headers={"Authorization": f"Bearer {token}"},
#                                       json=data)
#         destination_id = create_response.get_json()["id"]

#         delete_response = client.delete(f'/api/destinations/{destination_id}', 
#                                         headers={"Authorization": f"Bearer {token}"})

#         assert delete_response.status_code == 200
#         json_data = delete_response.get_json()
#         assert json_data["Message"].startswith("Destination deleted")
#         mock_delete_destination.assert_called_once()

#     # Test unauthorized access (no token)
#     def test_unauthorized_access(self, client):
#         response = client.get('/api/destinations/all')
#         assert response.status_code == 401
#         json_data = response.get_json()
#         assert json_data["Message"] == "Unauthorized, token missing"

#     # Test invalid token (JWT)
#     def test_invalid_token(self, client):
#         response = client.get('/api/destinations/all', 
#                               headers={"Authorization": "Bearer invalid_token"})
#         assert response.status_code == 401
#         json_data = response.get_json()
#         assert json_data["Message"] == "Invalid token"

#     # Test expired token (JWT)
#     def test_expired_token(self, client):
#         expired_token = jwt.encode({
#             "id": 1,
#             "email": "test@example.com",
#             "type": "Admin",
#             "exp": datetime.utcnow() - timedelta(seconds=1)  # Expired token
#         }, app.config['JWT_SECRET'], algorithm="HS256")

#         response = client.get('/api/destinations/all', 
#                               headers={"Authorization": f"Bearer {expired_token}"})
#         assert response.status_code == 401
#         json_data = response.get_json()
#         assert json_data["Message"] == "Token has expired"

#     # Test server error simulation (500)
#     def test_server_error(self, client):
#         with patch("app.save_destinations", side_effect=Exception("Database failure")):
#             token = generate_token(1, "Admin")
#             data = {
#                 "name": "New York",
#                 "description": "City in USA",
#                 "location": "America"
#             }

#             response = client.post('/api/destinations/create', 
#                                    headers={"Authorization": f"Bearer {token}"},
#                                    json=data)

#             assert response.status_code == 500
#             json_data = response.get_json()
#             assert json_data["Message"] == "Internal server error"