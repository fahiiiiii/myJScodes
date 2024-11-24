# Full Travel API

This API provides functionalities for managing users and destinations. It includes features for user registration, login, and profile management, as well as destination creation, retrieval, and deletion.

## Features

- **User Management**: Register, login, and manage user profiles.
- **Destination Management**: Create, view, and delete destinations (Admin only).
- **JWT Authentication**: Secure API endpoints using JSON Web Tokens (JWT).

## Endpoints

### User Service

#### Register a User
- **POST** `/api/users/register`
- Registers a new user with the provided name, email, password, and role.
  
**Request Body**:
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "password123",
  "role": "User"
}
Responses:

201: Registration successful
400: Invalid input or missing fields
409: Email already registered
Login a User
POST /api/users/login
Authenticates a user and returns an access token.
Request Body:

json
Copy code
{
  "email": "john@example.com",
  "password": "password123"
}
Responses:

200: Login successful, access token returned
401: Invalid credentials
Get User Profile
POST /api/users/profile
Retrieves the profile of the authenticated user using the access token.
Request Body:

json
Copy code
{
  "accessToken": "<your_jwt_token>"
}
Responses:

200: Profile retrieved successfully
400: Missing access token
401: Invalid or expired token
404: User not found
Destination Service
Get All Destinations
GET /api/destinations/all
Retrieves all available destinations.
Headers:

accessToken: JWT token for authentication
Responses:

200: List of destinations
403: Unauthorized, invalid or missing token
Create a Destination
POST /api/destinations/create
Allows an authenticated admin to create a new destination.
Request Body:

json
Copy code
{
  "name": "New York",
  "description": "The Big Apple",
  "location": "North America"
}
Headers:

Authorization: Bearer token for authentication
Responses:

201: Destination created successfully
403: Admin access required
400: Missing required fields
Get Destination by ID
GET /api/destinations/{id}
Retrieves the details of a destination by its ID.
Headers:

accessToken: JWT token for authentication
Responses:

200: Destination details
404: Destination not found
Delete a Destination
DELETE /api/destinations/{id}
Allows an admin to delete a destination by its ID.
Headers:

Authorization: Bearer token for authentication
Responses:

200: Destination deleted successfully
403: Admin access required
404: Destination not found
Authentication
All protected routes require a valid JWT access token. You can obtain a token by logging in with the /api/users/login endpoint.

To authenticate a request, add the token in the Authorization header as Bearer <token>.

Setup and Installation
Prerequisites
Python 3.8 or higher
Flask
Pytest (for testing)
Installation
Clone the repository:

bash
Copy code
git clone https://github.com/yourusername/full-travel-api.git
cd full-travel-api
Install the dependencies:

bash
Copy code
pip install -r requirements.txt
Set up environment variables (optional):

bash
Copy code
export FLASK_APP=app.py
export FLASK_ENV=development
Run the application:

bash
Copy code
flask run
The app will run on http://127.0.0.1:5000/.

Running Tests
To run the tests, use pytest:

bash
Copy code
pytest --cov=app --maxfail=1 --disable-warnings -v
This command will run the tests, show detailed output, and stop after the first failed test.

Error Codes
400: Bad Request — The request is malformed or missing required fields.
401: Unauthorized — Invalid or expired JWT token.
403: Forbidden — Insufficient permissions (e.g., trying to access admin endpoints as a non-admin user).
404: Not Found — The requested resource (user or destination) was not found.
409: Conflict — Resource already exists (e.g., duplicate email during registration).
500: Internal Server Error — An unexpected error occurred on the server.
License
This project is licensed under the MIT License - see the LICENSE file for details.

vbnet
Copy code

### How to Use:

1. **Set up** the environment and dependencies.
2. **Start the app** using Flask.
3. Use tools like Postman or cURL to make requests to the endpoints.
4. **Run tests** to ensure everything is functioning as expected.

Feel free to replace any project-specific information such as repository name, and you can further customize the content as necessary.






