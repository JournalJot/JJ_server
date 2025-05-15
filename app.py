from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import userData
import requests
import flask_bcrypt
import json
import logging
from flask_mail import Mail, Message
import os
from dotenv import load_dotenv
import random
import string
import base64


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["*"], "supports_credentials": True}})
bcrypt = flask_bcrypt.Bcrypt(app)
mail = Mail(app)


load_dotenv()

# Load environment variables
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['API_GEOLOCATION_KEY'] = os.getenv('API_GEOLOCATION_KEY')

@app.route('/api/location')
def get_location():
    try:
        api_key = app.config['API_GEOLOCATION_KEY']

        # Get the client's IP address
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ',' in ip:  # If multiple IPs are present, take the first one
            ip = ip.split(',')[0].strip()

        # Fetch location data using the client's IP
        location = requests.get(f"https://api.ipgeolocation.io/v2/ipgeo?apiKey={api_key}&ip={ip}&output=json")

        if location.status_code != 200:
            return jsonify({'error': 'Unable to fetch location data', 'error_code': location.status_code}), location.status_code

        return jsonify(location.json())
    except Exception as e:
        return jsonify({'error': 'An unexpected error occurred', 'details': str(e), 'error_code': 500}), 500


@app.route('/api/journal', methods=['POST', 'GET'])
def get_journal():
    if request.method == 'POST':
        try:
            # Check if the request is multipart/form-data (FormData from frontend)
            if request.content_type and request.content_type.startswith('multipart/form-data'):
                email = request.form.get('email')
                journal_body = request.form.get('journal_body')
                journal_title = request.form.get('journal_title')
                country = request.form.get('country')
                city = request.form.get('city')
                district = request.form.get('district')
                # Get file as bytes
                travel_pic_file = request.files.get('travel_pic')
                travel_pic = travel_pic_file.read() if travel_pic_file else None
                try:
                    latitude = float(request.form.get('latitude'))
                    longitude = float(request.form.get('longitude'))
                except (ValueError, TypeError) as e:
                    return jsonify({'error': 'Invalid latitude or longitude format', 'details': str(e), 'error_code': 400}), 400
            else:
                # Fallback to JSON
                if request.is_json:
                    data = request.get_json()
                else:
                    raw_data = request.data.decode('utf-8')
                    data = json.loads(raw_data)
                email = data.get('email')
                journal_body = data.get('journal_body')
                journal_title = data.get('journal_title')
                travel_pic = data.get('travel_pic')
                country = data.get('country')
                city = data.get('city')
                district = data.get('district')
                try:
                    latitude = float(data.get('latitude'))
                    longitude = float(data.get('longitude'))
                except (ValueError, TypeError) as e:
                    return jsonify({'error': 'Invalid latitude or longitude format', 'details': str(e), 'error_code': 400}), 400
        except Exception as e:
            return jsonify({'error': 'Invalid input format', 'details': str(e), 'error_code': 400}), 400

        # Insert journal data into the database
        userData.insertJournal(email, journal_body, journal_title, travel_pic, country, city, district, latitude, longitude)
        return jsonify({'message': 'Journal created successfully!', 'error_code': 201}), 201

    elif request.method == 'GET':
        email = request.args.get('email')
        if not email:
            return jsonify({'error': 'Email is required', 'error_code': 400}), 400

        journals = userData.getJournals(email)
        if not journals:
            return jsonify({'journals': [], 'error_code': 200}), 200

        journals_list = []
        for journal in journals:
            journal_dict = dict()
            # Adjust indices if your schema is different
            journal_dict['rowid'] = journal[0]
            journal_dict['email'] = journal[1]
            journal_dict['journal_body'] = journal[2]
            journal_dict['journal_title'] = journal[3]
            # Ready-to-use data URL for image
            if journal[4]:
                # Default to jpeg, change to png if you store pngs
                journal_dict['travel_pic'] = f"data:image/jpeg;base64,{base64.b64encode(journal[4]).decode('utf-8')}"
            else:
                journal_dict['travel_pic'] = None
            journal_dict['country'] = journal[5]
            journal_dict['city'] = journal[6]
            journal_dict['district'] = journal[7]
            journal_dict['latitude'] = journal[8]
            journal_dict['longitude'] = journal[9]
            journals_list.append(journal_dict)

        return jsonify({'journals': journals_list, 'error_code': 200}), 200


@app.route('/api/user', methods=['POST', 'GET'])
def create_user():
    if request.method == 'GET':
        email = request.args.get('email')
        if not email:
            return jsonify({'error': 'Email is required', 'error_code': 400}), 400
        data = userData.getData(email)
        if not data:
            return jsonify({'error': 'User not found', 'error_code': 404}), 404

        # Assuming data is a tuple: (rowid, Name, Email, Password, IsLoggedIn, Code, Profile_Pic)
        user_dict = {
            'rowid': data[0],
            'name': data[1],
            'email': data[2],
            # Do not include password in response for security!
            'is_logged_in': data[4],
            'code': data[5],
        }

        # Add profile_pic as a ready-to-use data URL if it exists
        if data[6]:
            user_dict['profile_pic'] = f"data:image/jpeg;base64,{base64.b64encode(data[6]).decode('utf-8')}"
        else:
            user_dict['profile_pic'] = None

        return jsonify({'user': user_dict, 'error_code': 200}), 200
    elif request.method == 'POST':
        try:
            if request.is_json:
                data = request.get_json()
            else:
                raw_data = request.data.decode('utf-8')
                data = json.loads(raw_data)
        except Exception as e:
            return jsonify({'error': 'Invalid JSON format', 'details': str(e), 'error_code': 400}), 400

        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        if userData.getData(email):
            return jsonify({'message': 'User already exists!', 'error_code': 409}), 409

        # Insert user data into the database
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        userData.insertData(name, email, password_hash)
        return jsonify({'message': 'User created successfully!', 'error_code': 201}), 201


@app.route("/api/login", methods=["POST"])
def login_user():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            raw_data = request.data.decode('utf-8')
            data = json.loads(raw_data)
    except Exception as e:
        return jsonify({'error': 'Invalid JSON format', 'details': str(e), 'error_code': 400}), 400

    email = data.get("email")
    password = data.get("password")

    # Retrieve user data from the database
    user = userData.getData(email)
    if not user:
        return jsonify({"message": "User not found!", "error_code": 404}), 404

    # Get the stored password hash
    password_hash = user[3]
    if not password_hash or not password_hash.startswith("$2b$"):
        return jsonify({"error": "Invalid password hash in database", "error_code": 500}), 500

    # Check if the password is correct
    try:
        if bcrypt.check_password_hash(password_hash, password):
            return jsonify({"message": "Login successful!", "error_code": 200}), 200
        else:
            return jsonify({"message": "Invalid password!", "error_code": 401}), 401
    except ValueError as e:
        logging.error(f"Error verifying password: {str(e)}")
        return jsonify({"error": "Password verification failed", "details": str(e), "error_code": 500}), 500


@app.route("/api/change_password", methods=["POST"])
def change_password():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            raw_data = request.data.decode('utf-8')
            data = json.loads(raw_data)
    except Exception as e:
        return jsonify({'error': 'Invalid JSON format', 'details': str(e), 'error_code': 400}), 400

    email = data.get("email")
    new_password = data.get("new_password")

    # Hash the new password
    new_password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')

    # Update the password in the database
    userData.changePassword(email, new_password_hash)

    return jsonify({"message": "Password changed successfully!", "error_code": 200}), 200


@app.route("/api/edit_journal", methods=["POST"])
def edit_journal():
    try:
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            rowid = request.form.get("rowid")
            email = request.form.get("email")
            journal_body = request.form.get("journal_body")
            journal_title = request.form.get("journal_title")
            country = request.form.get("country")
            city = request.form.get("city")
            district = request.form.get("district")
            travel_pic_file = request.files.get("travel_pic")
            travel_pic = travel_pic_file.read() if travel_pic_file else None
            try:
                latitude = float(request.form.get('latitude'))
                longitude = float(request.form.get('longitude'))
            except (ValueError, TypeError) as e:
                return jsonify({'error': 'Invalid latitude or longitude format', 'details': str(e), 'error_code': 400}), 400
        else:
            if request.is_json:
                data = request.get_json()
            else:
                raw_data = request.data.decode('utf-8')
                data = json.loads(raw_data)
            rowid = data.get("rowid")
            email = data.get("email")
            journal_body = data.get("journal_body")
            journal_title = data.get("journal_title")
            travel_pic = data.get("travel_pic")
            country = data.get("country")
            city = data.get("city")
            district = data.get("district")
            try:
                latitude = float(data.get('latitude'))
                longitude = float(data.get('longitude'))
            except (ValueError, TypeError) as e:
                return jsonify({'error': 'Invalid latitude or longitude format', 'details': str(e), 'error_code': 400}), 400

        # Update journal data in the database
        userData.editJournal(rowid, email, journal_body, journal_title, travel_pic, country, city, district, latitude, longitude)

        return jsonify({"message": "Journal updated successfully!", "error_code": 200}), 200
    except Exception as e:
        return jsonify({'error': 'Invalid input format', 'details': str(e), 'error_code': 400}), 400


@app.route("/api/delete_journal", methods=["POST"])
def delete_journal():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            raw_data = request.data.decode('utf-8')
            data = json.loads(raw_data)
    except Exception as e:
        return jsonify({'error': 'Invalid JSON format', 'details': str(e), 'error_code': 400}), 400

    rowid = data.get("rowid")
    email = data.get("email")

    # Delete journal data from the database
    userData.deleteJournal(rowid, email)

    return jsonify({"message": "Journal deleted successfully!", "error_code": 200}), 200


@app.route("/api/delete_user", methods=["POST"])
def delete_user():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            raw_data = request.data.decode('utf-8')
            data = json.loads(raw_data)
    except Exception as e:
        return jsonify({'error': 'Invalid JSON format', 'details': str(e), 'error_code': 400}), 400

    email = data.get("email")

    # Delete user data from the database
    userData.deleteUser(email)

    return jsonify({"message": "User deleted successfully!", "error_code": 200}), 200


@app.route("/api/forgot_password", methods=["POST"])
def forgot_password():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            raw_data = request.data.decode('utf-8')
            data = json.loads(raw_data)
    except Exception as e:
        return jsonify({'error': 'Invalid JSON format', 'details': str(e), 'error_code': 400}), 400

    email = data.get("email")
    if not email:
        return jsonify({'error': 'Email is required', 'error_code': 400}), 400

    # Generate a random 6-digit code
    code = ''.join(random.choices(string.digits, k=6))

    # Update the code in the database
    userData.setCode(email, code)
     
    # Send the code to the user's email
    try:
        msg = Message(
            subject="Your Password Reset Code",
            sender=app.config['MAIL_USERNAME'],
            recipients=[email],
            body=f"Your password reset code is: {code}"
        )
        mail.send(msg)
    except Exception as e:
        return jsonify({'error': 'Failed to send email', 'details': str(e), 'error_code': 500}), 500

    return jsonify({"message": "Code sent successfully!", "error_code": 200}), 200

@app.route("/api/verify_code", methods=["POST"])
def verify_code():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            raw_data = request.data.decode('utf-8')
            data = json.loads(raw_data)
    except Exception as e:
        return jsonify({'error': 'Invalid JSON format', 'details': str(e), 'error_code': 400}), 400

    email = data.get("email")
    code = data.get("code")

    # Verify the code in the database
    stored_code = userData.getCode(email)
    if not stored_code:
        return jsonify({'error': 'Code not found', 'error_code': 404}), 404
    if stored_code != code:
        return jsonify({'error': 'Invalid code', 'error_code': 401}), 401
    return jsonify({"message": "Code verified successfully!", "error_code": 200}), 200
    

@app.route("/api/profile_image", methods=["POST"])
def update_profile_pic():
    if not (request.content_type and request.content_type.startswith('multipart/form-data')):
        return jsonify({'error': 'Content-Type must be multipart/form-data', 'error_code': 400}), 400

    email = request.form.get("email")
    profile_pic_file = request.files.get("profile_pic")
    profile_pic = profile_pic_file.read() if profile_pic_file else None

    if not email or profile_pic is None:
        return jsonify({'error': 'Email and profile_pic are required', 'error_code': 400}), 400

    try:
        userData.updateProfilePic(email, profile_pic)
        return jsonify({"message": "Profile picture updated successfully!", "error_code": 200}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to update profile picture', 'details': str(e), 'error_code': 500}), 500


@app.errorhandler(Exception)
def handle_exception(e):
    logging.error(f"Unhandled Exception: {str(e)}")
    return jsonify({'error': 'An unexpected error occurred', 'details': str(e), 'error_code': 500}), 500



if __name__ == '__main__':
    app.run(host="0.0.0.0")
