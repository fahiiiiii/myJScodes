# # destinations_service/app.py


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



app = Flask(__name__)
load_dotenv()

# API configuration
api = Api(app, title="Destinations Microservice", version="1.0", description="Destinations Service API Documentation")
JWT_SECRET = os.getenv("JWT_SECRET", "default_secret_key")
DESTINATIONS_FILE = 'destinations.json'

# Auth parser for protected routes
auth_parser = api.parser()
auth_parser.add_argument('accessToken', type=str, location='headers', required=True, help='Authentication token')



def verify_token(access_token):
    if not access_token:
        return None, ("Unauthorized, token missing", 403)
    try:
        payload = jwt.decode(access_token, JWT_SECRET, algorithms=["HS256"])
        return payload, None
    except jwt.InvalidTokenError:
        return None, ("Invalid token", 403)

def verify_admin_token(access_token):
    payload, error = verify_token(access_token)
    if error:
        return None, error
    if payload.get("type") != "Admin":
        return None, ("Access Denied: Admin only", 403)
    return payload, None


from flask import Flask
from flask_restx import Api, Resource, fields
from flask import request, jsonify
import jwt
import os
import json
from dotenv import load_dotenv


# # API configuration
# api = Api(app, title="Destinations Microservice", version="1.0", description="Destinations Service API Documentation")
# JWT_SECRET = os.getenv("JWT_SECRET", "default_secret_key")
# DESTINATIONS_FILE = 'destinations.json'

# # Auth parser for protected routes
# auth_parser = api.parser()
# auth_parser.add_argument('accessToken', type=str, location='headers', required=True, help='Authentication token')

# Destination model
destination_model = api.model('Destination', {
    'id': fields.Integer(description='Destination ID'),
    'name': fields.String(description='Destination name'),
    'description': fields.String(description='Description'),
    'location': fields.String(description='Location'),
})

# Database operations
def load_destinations():
    if os.path.exists(DESTINATIONS_FILE):
        with open(DESTINATIONS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_destinations(destinations_db):
    with open(DESTINATIONS_FILE, 'w') as f:
        json.dump(destinations_db, f, indent=4)

def verify_token(access_token):
    if not access_token:
        return None, ("Unauthorized, token missing", 403)
    try:
        payload = jwt.decode(access_token, JWT_SECRET, algorithms=["HS256"])
        return payload, None
    except jwt.InvalidTokenError:
        return None, ("Invalid token", 403)

def verify_admin_token(access_token):
    payload, error = verify_token(access_token)
    if error:
        return None, error
    if payload.get("type") != "Admin":
        return None, ("Access Denied: Admin only", 403)
    return payload, None

# Initialize database
destinations_db = load_destinations()
next_destination_id = max(map(int, destinations_db.keys()), default=0) + 1

@api.route('/api/destinations/all')
class DestinationsResource(Resource):
    @api.expect(auth_parser)
    @api.marshal_list_with(destination_model)
    def get(self):
        # Verify token (any user type can view)
        payload, error = verify_token(request.headers.get('accessToken'))
        if error:
            return {"Message": error[0]}, error[1]
            
        return list(destinations_db.values()), 200



# First, create an authorization model
from flask_restx import Resource, fields, reqparse
from flask import request

# Define authorization header parser
authorization_parser = reqparse.RequestParser()
authorization_parser.add_argument('Authorization', location='headers', required=True, 
                                help='Format: Bearer <access_token>')

# Models
destination_model = api.model('Destination', {
    'id': fields.Integer(readonly=True),
    'name': fields.String(required=True, description='Destination name'),
    'description': fields.String(required=True, description='Description'),
    'location': fields.String(required=True, description='Location')
})

create_destination_model = api.model('CreateDestinationRequest', {
    'name': fields.String(required=True, description='Destination name'),
    'description': fields.String(required=True, description='Description'),
    'location': fields.String(required=True, description='Location')
})

# Helper function to extract token from Authorization header
def get_token_from_header():
    parser = authorization_parser.parse_args()
    auth_header = parser.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    return auth_header.split(' ')[1]

@api.route('/api/destinations/create')
class CreateDestinationResource(Resource):
    @api.expect(authorization_parser, create_destination_model)
    @api.response(201, 'Destination created successfully')
    @api.response(401, 'Unauthorized')
    @api.response(400, 'Bad Request')
    def post(self):
        global next_destination_id
        
        # Get token from header
        access_token = get_token_from_header()
        if not access_token:
            return {"Message": "Missing or invalid authorization header"}, 401
        
        # Verify admin access
        payload, error = verify_admin_token(access_token)
        if error:
            return {"Message": error[0]}, error[1]

        data = request.json
        if not all(key in data for key in ['name', 'description', 'location']):
            return {"Message": "Missing required fields"}, 400

        new_destination = {
            "id": next_destination_id,
            "name": data["name"],
            "description": data["description"],
            "location": data["location"]
        }

        destinations_db[str(next_destination_id)] = new_destination
        next_destination_id += 1
        save_destinations(destinations_db)

        return new_destination, 201

@api.route('/api/destinations/<int:id>')
class DestinationResource(Resource):
    @api.expect(authorization_parser)
    @api.response(200, 'Destination deleted successfully')
    @api.response(401, 'Unauthorized')
    @api.response(404, 'Destination not found')
    def delete(self, id):
        # Get token from header
        access_token = get_token_from_header()
        if not access_token:
            return {"Message": "Missing or invalid authorization header"}, 401
            
        # Verify admin access
        payload, error = verify_admin_token(access_token)
        if error:
            return {"Message": error[0]}, error[1]

        id_str = str(id)
        if id_str not in destinations_db:
            return {"Message": "Destination not found"}, 404

        deleted_name = destinations_db[id_str]['name']
        del destinations_db[id_str]
        save_destinations(destinations_db)

        return {
            "Message": f"Destination deleted : {deleted_name} "
        }, 200

    @api.expect(authorization_parser)
    @api.marshal_with(destination_model)
    @api.response(200, 'Success')
    @api.response(401, 'Unauthorized')
    @api.response(404, 'Destination not found')
    def get(self, id):
        # Get token from header
        access_token = get_token_from_header()
        if not access_token:
            return {"Message": "Missing or invalid authorization header"}, 401
            
        # Verify token (any user type can view)
        payload, error = verify_token(access_token)
        if error:
            return {"Message": error[0]}, error[1]

        id_str = str(id)
        if id_str not in destinations_db:
            return {"Message": "Destination not found"}, 404

        return destinations_db[id_str], 200

if __name__ == '__main__':
    app.run(port=5001)