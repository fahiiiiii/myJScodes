# routes/destinations.py
import jwt
from flask import Blueprint, request, jsonify
import os
import json
from dotenv import load_dotenv
from middleware.auth import authenticate_token

# Load environment variables
load_dotenv()

# Constants
JWT_SECRET = os.getenv("JWT_SECRET", "default_secret_key")
DESTINATIONS_FILE = 'destinations.json'

# Blueprint setup
destinations_blueprint = Blueprint('destinations', __name__)

def load_destinations():
    """Load destinations from the JSON file."""
    if os.path.exists(DESTINATIONS_FILE):
        with open(DESTINATIONS_FILE, "r") as file:
            return json.load(file)
    return {}

def save_destinations(destinations_db):
    """Save the destinations dictionary to the JSON file."""
    with open(DESTINATIONS_FILE, 'w') as f:
        json.dump(destinations_db, f, indent=4)

def verify_admin_token(access_token):
    """Verify the access token and check if the user is an admin."""
    if not access_token:
        return None, ("Unauthorized, token missing", 403)

    try:
        payload = jwt.decode(access_token, JWT_SECRET, algorithms=["HS256"])
        user_role = payload.get("type")
        
        if user_role != "Admin":
            return None, ("Access Denied: Only Admins are authorized for this action.", 403)
        
        return payload, None
        
    except jwt.ExpiredSignatureError:
        return None, ("Token expired", 403)
    except jwt.InvalidTokenError:
        return None, ("Invalid token", 403)

def validate_destination_data(data):
    """Validate the required fields for a destination."""
    required_fields = ["name", "description", "location"]
    
    for field in required_fields:
        if not data.get(field):
            return f"{field.capitalize()} is required", 400
    
    return None

# Initialize destinations database
destinations_db = load_destinations()
next_destination_id = max(map(int, destinations_db.keys()), default=0) + 1

@destinations_blueprint.route('/all_destinations', methods=['GET'])
def get_destinations():
    """Get all destinations."""
    return jsonify(list(destinations_db.values())), 200

@destinations_blueprint.route('/create_destination', methods=['POST'])
def add_destination():
    """Add a new destination (Admin only)."""
    global next_destination_id
    
    # Verify admin access
    payload, error = verify_admin_token(request.args.get('accessToken'))
    if error:
        return jsonify({"Message": error[0]}), error[1]
    
    # Validate input data
    data = request.json
    validation_error = validate_destination_data(data)
    if validation_error:
        return jsonify({"Message": validation_error[0]}), validation_error[1]
    
    # Create new destination
    new_destination = {
        "id": next_destination_id,
        "name": data["name"],
        "description": data["description"],
        "location": data["location"]
    }
    
    # Save to database
    destinations_db[str(next_destination_id)] = new_destination
    next_destination_id += 1
    save_destinations(destinations_db)
    
    return jsonify(new_destination), 201

@destinations_blueprint.route('/<int:id>', methods=['DELETE'])
def delete_destination(id):
    """Delete a destination (Admin only)."""
    # Verify admin access
    payload, error = verify_admin_token(request.args.get('accessToken'))
    if error:
        return jsonify({"Message": error[0]}), error[1]
    
    # Check if destination exists
    id_str = str(id)
    if id_str not in destinations_db:
        return jsonify({"Message": "Destination not found"}), 404
    
    # Delete destination
    deleted_name = destinations_db[id_str]['name']
    del destinations_db[id_str]
    save_destinations(destinations_db)
    
    return jsonify({
        "Message": f"Destination deleted: The name of the deleted destination is {deleted_name}"
    }), 200














    # import jwt  # Import the JWT module

# from flask import Blueprint, request, jsonify
# import os
# import json
# from dotenv import load_dotenv


# JWT_SECRET = os.getenv("JWT_SECRET", "default_secret_key")
# from middleware.auth import authenticate_token

# load_dotenv()
# load_dotenv()

# # JWT configuration
# JWT_SECRET = os.getenv("JWT_SECRET", "default_secret_key")

# # Blueprint for destinations
# destinations_blueprint = Blueprint('destinations', __name__)

# # File path for storing destinations
# DESTINATIONS_FILE = 'destinations.json'

# # Load destinations from the JSON file
# def load_destinations():
#     if os.path.exists(DESTINATIONS_FILE):
#         with open(DESTINATIONS_FILE, "r") as file:
#             return json.load(file)
#     return {}

# # Save destinations to the JSON file
# def save_destinations(destinations_db):
#     """Save the destinations dictionary to the JSON file."""
#     with open(DESTINATIONS_FILE, 'w') as f:
#         json.dump(destinations_db, f, indent=4)

# # Initialize destinations database
# destinations_db = load_destinations()

# # Set the next available ID for destinations
# next_destination_id = max(map(int, destinations_db.keys()), default=0) + 1
# # users_db = {}  # Simulating user data storage (use real DB in production)
# # destinations_db = {} 
# # Blueprint setup
# # destinations_blueprint = Blueprint('destinations', __name__)

# # Define the file where destinations will be stored
# # DESTINATIONS_FILE = 'destinations.json'

# # # Load destinations from the JSON file when the app starts
# # def load_destinations():
# #     if os.path.exists(DESTINATIONS_FILE):
# #         with open(DESTINATIONS_FILE, "r") as file:
# #             return json.load(file)
# #     return {}



# # # Save destinations to the JSON file
# # def save_destinations(destinations_db):
# #     """Save the destinations dictionary to the JSON file."""
# #     with open(DESTINATIONS_FILE, 'w') as f:
# #         json.dump(destinations_db, f, indent=4)

# # # In-memory destinations data
# # destinations_db = load_destinations()
# # next_destination_id = max(map(int, destinations_db.keys()), default=0) + 1  # Set the next available ID
# # destinations_blueprint = Blueprint('destinations', __name__)

# # # Get all destinations
# # @destinations_blueprint.route('/all_destinations', methods=['GET'])
# # def get_destinations():
# #     return jsonify(list(destinations_db.values())), 200

# # # Add a new destination
# # # @destinations_blueprint.route('/', methods=['POST'])
# # # @authenticate_token  # Ensure the user is authenticated before adding
# # # def add_destination():
# # #     global next_destination_id
# # #     user_role = request.user_payload.get("type")  # Get user role from JWT payload
# # #     if user_role != "Admin":
# # #         return jsonify({"Message": "Access Denied: Only Admins are authorized to create destinations."}), 403  # Only admins can add destinations

# # #     data = request.json  # Get the JSON data from the request

# # #     # Validate the input fields
# # #     if not data.get("name"):
# # #         return jsonify({"Message": "Name is required"}), 400
# # #     if not data.get("description"):
# # #         return jsonify({"Message": "Description is required"}), 400
# # #     if not data.get("location"):
# # #         return jsonify({"Message": "Location is required"}), 400
# # #     # if not data.get("price_per_night"):
# # #     #     return jsonify({"Message": "Price per night is required"}), 400

# # #     # Create new destination
# # #     new_destination = {
# # #         "id": next_destination_id,
# # #         "name": data["name"],
# # #         "description": data["description"],
# # #         "location": data["location"],
# # #         # "price_per_night": data["price_per_night"]
# # #     }

# # #     # Add the new destination to the database
# # #     destinations_db[next_destination_id] = new_destination
# # #     next_destination_id += 1

# # #     # Save the updated destinations data to the file
# # #     save_destinations(destinations_db)

# # #     return jsonify(new_destination), 201

# # from flask import request, jsonify

# # @destinations_blueprint.route('/', methods=['POST'])
# # @authenticate_token  # Use the authentication middleware here
# # def add_destination():
# #     global next_destination_id
# #     data = request.json  # Get the JSON data from the request
# #     access_token = request.args.get('accessToken')  # Retrieve access token from query
# #     if not access_token:
# #         return jsonify({"Message": "Unauthorized, token missing"}), 403

# #     # Decode the JWT token
# #     try:
# #         payload = jwt.decode(access_token, JWT_SECRET, algorithms=["HS256"])
# #         user_role = payload.get("type")  # Access user role from token
# #     except jwt.ExpiredSignatureError:
# #         return jsonify({"Message": "Token expired"}), 403
# #     except jwt.InvalidTokenError:
# #         return jsonify({"Message": "Invalid token"}), 403

# #     # Ensure only admin can create destinations
# #     if user_role != "Admin":
# #         return jsonify({"Message": "Access Denied: Only Admins are authorized to create destinations."}), 403


# #     # Validate the input fields
# #     if not data.get("name"):
# #         return jsonify({"Message": "Name is required"}), 400
# #     if not data.get("description"):
# #         return jsonify({"Message": "Description is required"}), 400
# #     if not data.get("location"):
# #         return jsonify({"Message": "Location is required"}), 400

# #     # Create new destination
# #     new_destination = {
# #         "id": next_destination_id,
# #         "name": data["name"],
# #         "description": data["description"],
# #         "location": data["location"]
# #     }

# #     # Add the new destination to the database
# #     destinations_db[next_destination_id] = new_destination
# #     next_destination_id += 1

# #     # Save the updated destinations data to the file
# #     save_destinations(destinations_db)

# #     return jsonify(new_destination), 201  # Return the newly created destination

# # DESTINATIONS_FILE = 'destinations.json'

# # # Load destinations from the JSON file when the app starts
# # def load_destinations():
# #     if os.path.exists(DESTINATIONS_FILE):
# #         with open(DESTINATIONS_FILE, "r") as file:
# #             return json.load(file)
# #     return {}

# # destinations_db = load_destinations()
# # next_destination_id = max(map(int, destinations_db.keys()), default=0) + 1  # Set the next available ID
# # # Save destinations to the JSON file
# # def save_destinations(destinations_db):
# #     """Save the destinations dictionary to the JSON file."""
# #     with open(DESTINATIONS_FILE, 'w') as f:
# #         json.dump(destinations_db, f, indent=4)

# # Initialize destinations_db and next_destination_id
# # next_destination_id = max(map(int, destinations_db.keys()), default=0) + 1  # Set the next available ID

# # Blueprint setup
# # destinations_blueprint = Blueprint('destinations', __name__)

# # Get all destinations
# @destinations_blueprint.route('/all_destinations', methods=['GET'])
# def get_destinations():
#     return jsonify(list(destinations_db.values())), 200

# # Add a new destination
# @destinations_blueprint.route('/', methods=['POST'])
# # @authenticate_token  # Ensure the user is authenticated before adding
# def add_destination():
#     # global next_destination_id  # Ensure the global variable is used
#     # global destinations_db
#     data = request.json  # Get the JSON data from the request
#     access_token = request.args.get('accessToken')  # Retrieve access token from query
#     if not access_token:
#         return jsonify({"Message": "Unauthorized, token missing"}), 403

#     # Decode the JWT token
#     try:
#         payload = jwt.decode(access_token, JWT_SECRET, algorithms=["HS256"])
#         user_role = payload.get("type")  # Access user role from token
#     except jwt.ExpiredSignatureError:
#         return jsonify({"Message": "Token expired"}), 403
#     except jwt.InvalidTokenError:
#         return jsonify({"Message": "Invalid token"}), 403

#     # Check if the user is authorized
#     if user_role != "Admin":
#         return jsonify({"Message": "Access Denied: Only Admins are authorized to create destinations."}), 403

#     # Validate the input fields
#     if not data.get("name"):
#         return jsonify({"Message": "Name is required"}), 400
#     if not data.get("description"):
#         return jsonify({"Message": "Description is required"}), 400
#     if not data.get("location"):
#         return jsonify({"Message": "Location is required"}), 400

#     # Create new destination
#     new_destination = {
#         "id": next_destination_id,
#         "name": data["name"],
#         "description": data["description"],
#         "location": data["location"]
#     }

#     # Add the new destination to the database
#     destinations_db[next_destination_id] = new_destination
#     next_destination_id += 1

#     # Save the updated destinations data to the file
#     save_destinations(destinations_db)

#     return jsonify(new_destination), 201  # Return the newly created destination




# @destinations_blueprint.route('/<int:id>', methods=['DELETE'])
# def delete_destination(id):
#     """
#     Delete a destination (Admin-only). Use 'accessToken' query parameter to authenticate.
#     """
#     access_token = request.args.get('accessToken')  # Retrieve access token from query
#     if not access_token:
#         return jsonify({"Message": "Unauthorized, token missing"}), 403

#     # Decode the JWT token
#     try:
#         payload = jwt.decode(access_token, JWT_SECRET, algorithms=["HS256"])
#         user_role = payload.get("type")  # Access user role from token
#     except jwt.ExpiredSignatureError:
#         return jsonify({"Message": "Token expired"}), 403
#     except jwt.InvalidTokenError:
#         return jsonify({"Message": "Invalid token"}), 403

#     # Check if the user is authorized
#     if user_role != "Admin":
#         return jsonify({"Message": "Access Denied: Only Admins are authorized to delete destinations."}), 403

#     # Convert ID to string to match the key format in destinations_db
#     id_str = str(id)

#     # Check if the destination exists
#     if id_str not in destinations_db:
#         return jsonify({"Message": "Destination not found"}), 404
#     role_msg = f"Destination deleted and the destination was {data['name']}"

#     # Delete the destination
#     del destinations_db[id_str]
#     save_destinations(destinations_db)

#     return {
#         "Message": role_msg
#     }, 200


