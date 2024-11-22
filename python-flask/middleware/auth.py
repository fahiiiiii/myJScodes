# middleware/auth.py
import jwt
from flask import request, jsonify
import os
from functools import wraps
from dotenv import load_dotenv
load_dotenv()

# Load the JWT_SECRET from environment variables
JWT_SECRET = os.getenv("JWT_SECRET")
print(f"JWT_SECRET is: {JWT_SECRET}")

def authenticate_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_headers = request.headers.get('Authorization')
        
        # Check if Authorization header is present
        if not auth_headers:
            return jsonify({"Message": "Token missing"}), 401
        
        # Try splitting the header to get the token
        parts = auth_headers.split(" ")
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"Message": "Invalid token format"}), 401
        
        token = parts[1]
        
        # Validate if token is present
        if not token:
            return jsonify({"Message": "Unauthorized"}), 401

        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            print("Decoded Payload:", payload)  # Log payload
            request.user_payload = payload  # Add payload to the request object
        except jwt.ExpiredSignatureError:
            return jsonify({"Message": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"Message": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated_function
