# user_service.py
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import jwt
from datetime import datetime, timedelta

app = Flask(__name__)
JWT_SECRET = 'your_secret_key'

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT,
        role TEXT)''')
    conn.commit()
    conn.close()

@app.route('/api/users/register', methods=['POST'])
def register_user():
    data = request.get_json()
    name = data['name']
    email = data['email']
    password = generate_password_hash(data['password'])
    role = data['role']

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)', 
                   (name, email, password, role))
    conn.commit()
    conn.close()

    return jsonify({"Message": "User registered successfully!"}), 201

@app.route('/api/users/login', methods=['POST'])
def login_user():
    data = request.get_json()
    email = data['email']
    password = data['password']

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email=?', (email,))
    user = cursor.fetchone()
    conn.close()

    if user and check_password_hash(user[2], password):
        token = jwt.encode({'id': user[0], 'email': user[1], 'role': user[4], 
                            'exp': datetime.utcnow() + timedelta(hours=1)}, JWT_SECRET, algorithm="HS256")
        return jsonify({"accessToken": token}), 200
    else:
        return jsonify({"Message": "Invalid credentials"}), 401

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)
