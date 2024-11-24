

# # users_service/app.py


from flask import Flask
from flask_restx import Api, Resource, fields
from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import os
import json
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Initialize Flask app for Users Service
app = Flask(__name__)
load_dotenv()

# API configuration
api = Api(app, title="Users Microservice", version="1.0", description="Users Service API Documentation")
JWT_SECRET = os.getenv("JWT_SECRET", "default_secret_key")
USERS_FILE = 'users.json'

# User models
user_model = api.model('User', {
    'id': fields.Integer(description='User ID'),
    'email': fields.String(description='User email address'),
    'name': fields.String(description='User full name'),
    'type': fields.String(description='User type (Admin/User)'),
})

register_model = api.model('RegisterRequest', {
    'name': fields.String(required=True, description='User full name', example='John Doe'),
    'email': fields.String(required=True, description='User email address', example='john@example.com'),
    'password': fields.String(required=True, description='User password', example='password123'),
    'role': fields.String(required=True, description='User role (Admin/User)', example="'Type 'User'' or 'Admin'")
})

login_model = api.model('LoginRequest', {
    'email': fields.String(required=True, description='User email address', example='john@example.com'),
    'password': fields.String(required=True, description='User password', example='password123')
})

profile_model = api.model('ProfileRequest', {
    'accessToken': fields.String(required=True, description='JWT token received after login', 
                               example='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...')
})

# Database operations
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users_db):
    with open(USERS_FILE, 'w') as f:
        json.dump(users_db, f, indent=4)

# Initialize database
users_db = load_users()
next_user_id = max(map(int, users_db.keys()), default=0) + 1

# User endpoints
@api.route('/api/users/register')
class RegisterResource(Resource):
    @api.doc(description='Register a new user')
    @api.expect(register_model)
    @api.response(201, 'Success - User registered successfully')
    @api.response(400, 'Bad Request - Invalid input')
    @api.response(409, 'Conflict - Email already registered')
    def post(self):
        """
        Register a new user
        
        Provide user details to create a new account. The role must be either 'Admin' or 'User'.
        """
        global next_user_id
        data = request.json

        # Validation
        if not all(key in data for key in ['name', 'email', 'password', 'role']):
            return {"Message": "Missing required fields"}, 400

        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, data["email"]):
            return {"Message": "Invalid email format"}, 400

        if any(u['email'] == data['email'] for u in users_db.values()):
            return {"Message": "Email already registered"}, 409

        if data.get("role") not in ["Admin", "User"]:
            return {"Message": "Invalid role"}, 400

        # Create new user
        hashed_password = generate_password_hash(data["password"])
        new_user = {
            "id": next_user_id,
            "name": data["name"],
            "email": data["email"],
            "password": hashed_password,
            "type": data["role"]
        }

        users_db[str(next_user_id)] = new_user
        next_user_id += 1
        save_users(users_db)

        return {
            "Message": f"Registration successful as {data['role']}",
            "User": {k: v for k, v in new_user.items() if k != "password"}
        }, 201

@api.route('/api/users/login')
class LoginResource(Resource):
    @api.doc(description='Login user and get access token')
    @api.expect(login_model)
    @api.response(200, 'Success - Login successful')
    @api.response(401, 'Unauthorized - Invalid credentials')
    def post(self):
        """
        Login with user credentials
        
        Provide email and password to receive an access token.
        """
        data = request.json
        user = next((u for u in users_db.values() if u["email"] == data.get("email")), None)

        if not user or not check_password_hash(user["password"], data.get("password")):
            return {"Message": "Invalid credentials"}, 401

        token = jwt.encode({
            "id": user["id"],
            "email": user["email"],
            "type": user["type"],
            "exp": datetime.utcnow() + timedelta(hours=3)
        }, JWT_SECRET, algorithm="HS256")

        return {"accessToken": token}, 200

@api.route('/api/users/profile')
class ProfileResource(Resource):
    @api.doc(description='Get user profile using access token')
    @api.expect(profile_model)
    @api.response(200, 'Success - Profile retrieved successfully')
    @api.response(400, 'Bad Request - Missing access token')
    @api.response(401, 'Unauthorized - Invalid or expired token')
    @api.response(404, 'Not Found - User not found')
    def post(self):
        """
        Get user profile information using access token
        
        Provide the JWT access token that you received after login to get your profile details.
        """
        data = request.json

        # Validation
        if not data.get("accessToken"):
            return {"Message": "Missing access token"}, 400

        try:
            # Verify token
            decoded_token = jwt.decode(data["accessToken"], JWT_SECRET, algorithms=["HS256"])
            user = next((u for u in users_db.values() if u["id"] == decoded_token["id"]), None)

            if not user:
                return {"Message": "User not found"}, 404

            return {
                "Message": "Profile retrieved successfully",
                "User": {
                    "id": user["id"],
                    "name": user["name"],
                    "email": user["email"],
                    "type": user["type"]
                }
            }, 200

        except jwt.ExpiredSignatureError:
            return {"Message": "Token has expired"}, 401
        except jwt.InvalidTokenError:
            return {"Message": "Invalid token"}, 401

if __name__ == '__main__':
    app.run(port=5000)