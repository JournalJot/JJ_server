from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import userData
import requests
import flask_bcrypt
import json
import logging

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["*"], "supports_credentials": True}})
bcrypt = flask_bcrypt.Bcrypt(app)


@app.route('/api/location')
def get_location():
    api_key = "c1cbfc5ed14e469a9c029e0700e69400"
    
    # Get the client's IP address
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ',' in ip:  # If multiple IPs are present, take the first one
        ip = ip.split(',')[0].strip()
    
    # Fetch location data using the client's IP
    location = requests.get(f"https://api.ipgeolocation.io/v2/ipgeo?apiKey={api_key}&ip={ip}&output=json")
    
    if location.status_code != 200:
        return jsonify({'error': 'Unable to fetch location data'}), location.status_code
    
    return jsonify(location.json())


@app.route('/api/journal', methods=['POST', 'GET'])
def get_journal():
    if request.method == 'POST':
        # Handle JSON or raw data
        try:
            if request.is_json:
                data = request.get_json()
            else:
                raw_data = request.data.decode('utf-8')
                data = json.loads(raw_data)
        except Exception as e:
            return jsonify({'error': 'Invalid JSON format', 'details': str(e)}), 400

        # Extract fields
        email = data.get('email')
        journal_body = data.get('journal_body')
        journal_title = data.get('journal_title')
        travel_pic = data.get('travel_pic')
        country = data.get('country')
        city = data.get('city')
        district = data.get('district')

        # Convert latitude and longitude to floats
        try:
            latitude = float(data.get('latitude'))
            longitude = float(data.get('longitude'))
        except ValueError as e:
            return jsonify({'error': 'Invalid latitude or longitude format', 'details': str(e)}), 400

        # Insert journal data into the database
        userData.insertJournal(email, journal_body, journal_title, travel_pic, country, city, district, latitude, longitude)
        return jsonify({'message': 'Journal created successfully!'})

    elif request.method == 'GET':
        # Handle query parameters
        email = request.args.get('email')  # Get 'email' from query parameters
        if not email:
            return jsonify({'error': 'Email is required'}), 400

        # Fetch journals from the database
        journals = userData.getJournals(email)
        return jsonify(journals)


@app.route('/api/user', methods=['POST'])
def create_user():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            raw_data = request.data.decode('utf-8')
            data = json.loads(raw_data)
    except Exception as e:
        return jsonify({'error': 'Invalid JSON format', 'details': str(e)}), 400

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    if userData.getData(email):
        return jsonify({'message': 'User already exists!'})

    # Insert user data into the database
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    userData.insertData(name, email, password_hash)
    return jsonify({'message': 'User created successfully!'})


@app.route("/api/login", methods=["POST"])
def login_user():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            raw_data = request.data.decode('utf-8')
            data = json.loads(raw_data)
    except Exception as e:
        return jsonify({'error': 'Invalid JSON format', 'details': str(e)}), 400

    email = data.get("email")
    password = data.get("password")

    user = userData.getData(email)
    if not user:
        return jsonify({"message": "User not found!"})

    # Check if the password is correct
    if bcrypt.check_password_hash(user[2], password):
        return jsonify({"message": "Login successful!"})
    else:
        return jsonify({"message": "Invalid password!"})


@app.route("/api/change_password", methods=["POST"])
def change_password():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            raw_data = request.data.decode('utf-8')
            data = json.loads(raw_data)
    except Exception as e:
        return jsonify({'error': 'Invalid JSON format', 'details': str(e)}), 400

    email = data.get("email")
    new_password = data.get("new_password")

    # Hash the new password
    new_password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')

    # Update the password in the database
    userData.changePassword(email, new_password_hash)

    return jsonify({"message": "Password changed successfully!"})


@app.route("/api/edit_journal", methods=["POST"])
def edit_journal():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            raw_data = request.data.decode('utf-8')
            data = json.loads(raw_data)
    except Exception as e:
        return jsonify({'error': 'Invalid JSON format', 'details': str(e)}), 400

    rowid = data.get("rowid")
    email = data.get("email")
    journal_body = data.get("journal_body")
    journal_title = data.get("journal_title")
    travel_pic = data.get("travel_pic")
    country = data.get("country")
    city = data.get("city")
    district = data.get("district")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    # Update journal data in the database
    userData.editJournal(rowid, email, journal_body, journal_title, travel_pic, country, city, district, latitude, longitude)

    return jsonify({"message": "Journal updated successfully!"})


@app.route("/api/delete_journal", methods=["POST"])
def delete_journal():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            raw_data = request.data.decode('utf-8')
            data = json.loads(raw_data)
    except Exception as e:
        return jsonify({'error': 'Invalid JSON format', 'details': str(e)}), 400

    rowid = data.get("rowid")
    email = data.get("email")

    # Delete journal data from the database
    userData.deleteJournal(rowid, email)

    return jsonify({"message": "Journal deleted successfully!"})


@app.route("/api/delete_user", methods=["POST"])
def delete_user():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            raw_data = request.data.decode('utf-8')
            data = json.loads(raw_data)
    except Exception as e:
        return jsonify({'error': 'Invalid JSON format', 'details': str(e)}), 400

    email = data.get("email")

    # Delete user data from the database
    userData.deleteUser(email)

    return jsonify({"message": "User deleted successfully!"})

@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled Exception: {str(e)}")
    return jsonify({'error': 'An unexpected error occurred', 'details': str(e)}), 500


if __name__ == '__main__':
    app.run(host="0.0.0.0")
