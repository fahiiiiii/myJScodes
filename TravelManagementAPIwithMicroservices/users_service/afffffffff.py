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
    @api.expect(api.model('RegisterRequest', {
        'name': fields.String(required=True),
        'email': fields.String(required=True),
        'password': fields.String(required=True),
        'role': fields.String(required=True),
    }))
    def post(self):
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
    @api.expect(api.model('LoginRequest', {
        'email': fields.String(required=True),
        'password': fields.String(required=True),
    }))
    def post(self):
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








if __name__ == '__main__':
    app.run(port=5000)







