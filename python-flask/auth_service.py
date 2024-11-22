# auth_service.py
import jwt
from datetime import datetime, timedelta
from flask import Flask, jsonify, request

app = Flask(__name__)
JWT_SECRET = 'your_secret_key'

@app.route('/api/auth/token', methods=['POST'])
def generate_token():
    data = request.get_json()
    user_id = data.get('id')
    email = data.get('email')
    role = data.get('role')

    token = jwt.encode({'id': user_id, 'email': email, 'role': role, 
                        'exp': datetime.utcnow() + timedelta(hours=1)}, JWT_SECRET, algorithm="HS256")
    return jsonify({"accessToken": token}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5003)
