
from flask import Flask
from flask_restx import Api, Resource, fields
from routes.destinations import destinations_blueprint

from routes.users import users_blueprint
import os
from dotenv import load_dotenv
# from middleware.auth import authenticate_token

# Initialize Flask app
app = Flask(__name__)
load_dotenv()

# Get the JWT secret from environment variables
JWT_SECRET = os.getenv("JWT_SECRET")
# print(f"JWT_SECRET app: {JWT_SECRET}")
next_destination_id = 1
# Initialize API with Swagger UI
api = Api(app, title="My Flask API", version="1.0", description="Dynamic API Documentation")

# Register Blueprints
app.register_blueprint(destinations_blueprint, url_prefix='/api/destinations')
app.register_blueprint(users_blueprint, url_prefix='/api/users')

# Define Models and Endpoints for Swagger UI

# Example User Model
user_model = api.model('User', {
    'id': fields.Integer(description='User ID'),
    'email': fields.String(description='User email address'),
    'name': fields.String(description='User full name'),
    'type': fields.String(description='User type (Admin/User)'),
})

# Define destination model
destination_model = api.model('Destination', {
    'id': fields.Integer(description='Destination ID'),
    'name': fields.String(description='Destination name'),
    'description': fields.String(description='Description of the destination'),
    'location': fields.String(description='Location of the destination'),
})


@api.route('/api/users/register')
class RegisterResource(Resource):
    @api.expect(api.model('RegisterRequest', {
        'name': fields.String(required=True, description='User full name'),
        'email': fields.String(required=True, description='User email'),
        'password': fields.String(required=True, description='User password'),
        'role': fields.String(required=True, description='Role (Admin/User)'),
    }))
    @api.response(201, 'User successfully registered')
    @api.response(409, 'Email already registered')
    @api.response(400, 'Invalid role')
    def post(self):
        """Register a new user"""
        data = request.json

        # Check if email is already registered
        if any(u['email'] == data['email'] for u in users_db.values()):
            return {"Message": "Email already registered"}, 409

        # Validate role
        if data.get("role") not in ["Admin", "User"]:
            return {"Message": "Invalid role. Role must be 'Admin' or 'User'"}, 400

        # Hash the password using a valid hashing method
        hashed_password = generate_password_hash(data["password"], method="pbkdf2:sha256")

        # Create new user
        global next_user_id
        new_user = {
            "id": next_user_id,
            "name": data["name"],
            "email": data["email"],
            "password": hashed_password,
            "type": data["role"],
        }
        users_db[next_user_id] = new_user
        next_user_id += 1

        # Save users (optional)
        save_users(users_db)

        return {
            "Message": f"Your registration as {data['role']} is successful.",
            "User": {key: value for key, value in new_user.items() if key != "password"}
        }, 201



# Example /login endpoint
@api.route('/api/users/login')
class LoginResource(Resource):
    @api.expect(api.model('LoginRequest', {
        'email': fields.String(required=True, description='User email'),
        'password': fields.String(required=True, description='User password'),
    }))
    @api.response(200, 'Success', model=api.model('TokenResponse', {
        'accessToken': fields.String(description='JWT access token'),
    }))
    @api.response(401, 'Invalid credentials')
    def post(self):
        """Authenticate user and return a JWT token."""
        return {"accessToken": "example.jwt.token"}, 200


import jwt
from flask import request, jsonify
from flask_restx import Resource, fields
import os

# JWT secret from environment variables
JWT_SECRET = os.getenv("JWT_SECRET", "default_secret_key")

# User model for Swagger documentation
user_model = api.model('User', {
    'id': fields.Integer(description='User ID'),
    'email': fields.String(description='User email address'),
    'name': fields.String(description='User full name'),
    'type': fields.String(description='User type (Admin/User)'),
})

# In-memory users database (replace with your actual database)
users_db = {
    1: {"id": 1, "email": "test@example.com", "name": "Test User", "type": "Admin"}
}
destinations_db={
    
}


@api.route('/api/users/profile')
class ProfileResource(Resource):
    @api.doc(params={'accessToken': 'JWT access token for authentication'})
    @api.response(200, 'Success', model=user_model)
    @api.response(401, 'Unauthorized')
    @api.response(404, 'User not found')
    def get(self):
        """Get the profile of the currently authenticated user."""
        # Manually input the access token as a query parameter
        token = request.args.get('accessToken')  # Access token passed as query parameter

        if not token:
            return {"Message": "Unauthorized, token missing"}, 401

        try:
            # Decode the token
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            user_id = payload.get("id")
            
            # Retrieve user data
            user = users_db.get(user_id)
            if not user:
                return {"Message": "User not found"}, 404

            # Exclude sensitive fields like password if applicable
            return {key: value for key, value in user.items()}, 200

        except jwt.ExpiredSignatureError:
            return {"Message": "Token expired"}, 401
        except jwt.InvalidTokenError:
            return {"Message": "Invalid token"}, 401







# GET /api/destinations endpoint to retrieve all destinations
@api.route('/api/destinations/all_destinations')
class DestinationsListResource(Resource):
    @api.doc('get_all_destinations')
    @api.marshal_list_with(destination_model)  # Define what fields to return in the response
    def get(self):
        """Get all destinations."""
        return list(destinations_db.values()), 200

@api.route('/api/destinations//create_destination')
class CreateDestinationResource(Resource):
    @api.expect(api.model('DestinationRequest', {
        'name': fields.String(required=True, description='Destination name'),
        'description': fields.String(required=True, description='Description of the destination'),
        'location': fields.String(required=True, description='Location of the destination'),
    }))
    @api.response(201, 'Destination created successfully')
    @api.response(400, 'Invalid input data')
    @api.response(403, 'Unauthorized, Admin role required')
    @api.response(401, 'Unauthorized, invalid token')
    @api.doc(params={'accessToken': 'JWT access token for authentication'})
    def post(self):
        """Create a new destination (Admin-only)"""
        access_token = request.args.get('accessToken')  # Retrieve the access token
        if not access_token:
            return {"Message": "Unauthorized, token missing"}, 403
        
        # Decode the access token
        try:
            payload = jwt.decode(access_token, JWT_SECRET, algorithms=["HS256"])
            user_role = payload.get("type")  # Retrieve user role from token
        except jwt.ExpiredSignatureError:
            return {"Message": "Token expired"}, 403
        except jwt.InvalidTokenError:
            return {"Message": "Invalid token"}, 403
        
        # Check if the user is authorized
        if user_role != "Admin":
            return {"Message": "Access Denied: Only Admins are authorized to delete destinations."}, 403

        # Extract destination data from request
        data = request.json

        # Validate destination data
        if not data.get("name") or not data.get("description") or not data.get("location"):
            return {"Message": "Invalid data. Name, description, and location are required."}, 400

        # Create the destination
        global next_destination_id
        new_destination = {
            "id": next_destination_id,
            "name": data["name"],
            "description": data["description"],
            "location": data["location"],
        }

        destinations_db[next_destination_id] = new_destination
        next_destination_id += 1
        save_destinations(destinations_db)
        # Save destinations (optional)
        # save_destinations(destinations_db)

        return {
            "Message": "Destination created successfully.",
            "Destination": {key: value for key, value in new_destination.items()}
        }, 201


# DELETE /api/destinations/<id> endpoint to delete a destination
@api.route('/api/destinations/<int:id>')
class DeleteDestination(Resource):
    @api.response(200, "Destination deleted")
    @api.response(404, "Destination not found")
    @api.response(403, "Unauthorized")
    @api.doc(params={'accessToken': 'JWT access token for authentication'})
    def delete(self, id):
        """Delete a destination (Admin-only)."""
        access_token = request.args.get('accessToken')  # Retrieve the access token
        if not access_token:
            return {"Message": "Unauthorized, token missing"}, 403
        
        # Decode the access token
        try:
            payload = jwt.decode(access_token, JWT_SECRET, algorithms=["HS256"])
            user_role = payload.get("type")  # Retrieve user role from token
        except jwt.ExpiredSignatureError:
            return {"Message": "Token expired"}, 403
        except jwt.InvalidTokenError:
            return {"Message": "Invalid token"}, 403
        
        # Check if the user is authorized
        if user_role != "Admin":
            return {"Message": "Access Denied: Only Admins are authorized to delete destinations."}, 403


        # Check if the destination exists
        if id not in destinations_db:
            return {"Message": "Destination not found"}, 404
        # role_msg = f"Destination deleted and the destination was {data['name']}"
        # Delete the destination
        del destinations_db[id]
        save_destinations(destinations_db)
        return {
            "Message": f"Destination deleted and the destination was {data['name']}"

        } , 200



if __name__ == '__main__':
    app.run(debug=True)
