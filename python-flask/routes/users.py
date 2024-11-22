# routes/users.py
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import os
from dotenv import load_dotenv
import json
import jwt
import re
from datetime import datetime, timedelta
# from werkzeug.security import generate_password_hash
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
from middleware.auth import authenticate_token

# Load environment variables from the .env file

load_dotenv()

# Now you can use the SECRET_KEY from the environment
JWT_SECRET = os.getenv("JWT_SECRET")
print(f"JWT_SECRET: {JWT_SECRET}")
# Define the file where users will be stored
USERS_FILE = 'users.json'

# Load users from a JSON file when the app starts
def load_users():
    """Load users from the JSON file into the dictionary."""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)  # Load data from the file
    return {}  # Return empty dict if file is not found or JSON is invalid

# Save users to the JSON file
def save_users(users_db):
    """Save the users dictionary to the JSON file."""
    with open(USERS_FILE, 'w') as f:
        json.dump(users_db, f, indent=4)


users_blueprint = Blueprint('users', __name__)
# Initialize the users data by loading from the JSON file
users_db = load_users()

# Ensure the next user ID is correctly set by converting keys to integers
next_user_id = max(map(int, users_db.keys()), default=0) + 1  # Set the next available ID


@users_blueprint.route('/register', methods=['POST'])
def register_user():
    global next_user_id
    data = request.json  # Get the JSON data from the request

    # Validate input fields
    if not data.get("name"):
        return jsonify({"Message": "Name is required"}), 400
    if not data.get("email"):
        return jsonify({"Message": "Email is required"}), 400
    if not data.get("password"):
        return jsonify({"Message": "Password is required"}), 400
    if not data.get("role"):
        return jsonify({"Message": "Role is required"}), 400

    # Check if email is in valid format
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if not re.match(email_regex, data["email"]):
        return jsonify({"Message": "Invalid email format"}), 400

    # Check if email is already registered
    if any(u['email'] == data['email'] for u in users_db.values()):
        return jsonify({"Message": "Email already registered"}), 409

    # Check password length
    if len(data["password"]) < 6:
        return jsonify({"Message": "Password must be at least 6 characters long"}), 400

    # Validate role
    if data.get("role") not in ["Admin", "User"]:
        return jsonify({"Message": "Invalid role. Role must be 'Admin' or 'User'"}), 400

    # Hash the password using a valid hashing method
    hashed_password = generate_password_hash(data["password"], method="pbkdf2:sha256")

    # Create new user
    new_user = {
        "id": next_user_id,
        "name": data["name"],
        "email": data["email"],
        "password": hashed_password,  # Store the hashed password
        "type": data["role"]
    }

    # Add new user to the dictionary
    users_db[next_user_id] = new_user
    next_user_id += 1

    # Save the updated users data to the file
    save_users(users_db)

    # Generate a custom success message based on role
    role_message = f"Your registration as {data['role']} is successful."

    return jsonify({
        "Message": role_message,
        "User": {key: value for key, value in new_user.items() if key != "password"}  # Exclude the password
    }), 201


# Login user
@users_blueprint.route('/login', methods=['POST'])
def login_user():
    data = request.json
    user = next((u for u in users_db.values() if u["email"] == data.get("email")), None)

    if not user or not check_password_hash(user["password"], data.get("password")):
        return jsonify({"Message": "Invalid credentials"}), 401

    payload = {
        "id": user["id"],
        "email": user["email"],
        "type": user["type"],
        "exp": datetime.utcnow() + timedelta(hours=3)
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return jsonify({"accessToken": token}), 200






from functools import wraps
# Define a simple 404 error message
def error_message_for_404():
    return jsonify({"Message": "User not found"}), 404

# Define a simple function to catch errors
def catch_error_message(error):
    return jsonify({"Message": f"An error occurred: {str(error)}"}), 500





@users_blueprint.route('/profile', methods=['GET'])
def view_profile():
    try:
        # Retrieve accessToken from query parameters for manual input in Swagger
        token = request.args.get('accessToken')
        if not token:
            return jsonify({"Message": "Unauthorized, token missing"}), 401

        # Decode the token and attach payload
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            print("Decoded Payload:", payload)
        except jwt.ExpiredSignatureError:
            return jsonify({"Message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"Message": "Invalid token"}), 401

        # Extract user_id from the token payload
        user_id = str(payload.get("id"))  # Convert id to string to match users_db keys
        if not user_id:
            return jsonify({"Message": "User ID not found in token"}), 401
        print(f"Looking for user ID {user_id} in users_db")

        # Check if user exists in the database
        user = users_db.get(user_id)
        if not user:
            return jsonify({"Message": "User not found"}), 404

        # Exclude sensitive data and return the response
        return jsonify({key: value for key, value in user.items() if key != "password"}), 200

    except Exception as error:
        print(f"Error: {error}")
        return jsonify({"Message": f"An error occurred: {str(error)}"}), 500



print(users_db)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
