
# gateway.py
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

USER_SERVICE_URL = 'http://user_service:5001'
DEST_SERVICE_URL = 'http://destination_service:5002'
AUTH_SERVICE_URL = 'http://auth_service:5003'

@app.route('/api/users/register', methods=['POST'])
def register_user():
    response = requests.post(f'{USER_SERVICE_URL}/api/users/register', json=request.get_json())
    return jsonify(response.json()), response.status_code

@app.route('/api/users/login', methods=['POST'])
def login_user():
    response = requests.post(f'{USER_SERVICE_URL}/api/users/login', json=request.get_json())
    return jsonify(response.json()), response.status_code

@app.route('/api/destinations/all', methods=['GET'])
def get_destinations():
    response = requests.get(f'{DEST_SERVICE_URL}/api/destinations/all')
    return jsonify(response.json()), response.status_code

@app.route('/api/destinations', methods=['POST'])
def create_destination():
    response = requests.post(f'{DEST_SERVICE_URL}/api/destinations', json=request.get_json())
    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(debug=True, port=5000)
