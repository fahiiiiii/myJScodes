# destination_service.py
from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('destinations.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS destinations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        location TEXT)''')
    conn.commit()
    conn.close()

@app.route('/api/destinations/all', methods=['GET'])
def get_destinations():
    conn = sqlite3.connect('destinations.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM destinations')
    destinations = cursor.fetchall()
    conn.close()
    
    return jsonify(destinations), 200

@app.route('/api/destinations', methods=['POST'])
def create_destination():
    data = request.get_json()
    name = data['name']
    description = data['description']
    location = data['location']

    conn = sqlite3.connect('destinations.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO destinations (name, description, location) VALUES (?, ?, ?)', 
                   (name, description, location))
    conn.commit()
    conn.close()

    return jsonify({"Message": "Destination created successfully."}), 201

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5002)
