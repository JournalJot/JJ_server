from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import userData
import requests
import flask_bcrypt

app = Flask(__name__)
cors = CORS(app, resources={r"*": {"origins": "https://journaljot-o7hvvkiiu-ademola-abdulsamad-afolabis-projects.vercel.app/"}})
bcrypt = flask_bcrypt.Bcrypt(app)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/location', methods=['GET'])
def get_location():
    api_key = "c2d63ce1a4764c03a7876a7fbe6146eb"
    ip = request.remote_addr 
    location = requests.get("https://api.ipgeolocation.io/v2/ipgeo?apiKey=" + api_key + "&ip=" + ip + "&output=json")
    if location.status_code != 200:
        return jsonify({'error': 'Unable to fetch location data'}), 500
    return location.json()
# Endpoint URL = 'https://api.ipgeolocation.io/v2/ipgeo?apiKey=API_KEY&ip=1.1.1.1&fields=location.city&output=xml'

@app.route('/api/journal', methods=['POST','GET'])
def get_journal():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        journal_body = data.get('journal_body')
        journal_title = data.get('journal_title')
        travel_pic = data.get('travel_pic')
        country = data.get('country')
        city = data.get('city')
        district = data.get('district')
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        # Insert journal data into the database
        userData.insertJournal(email, journal_body, journal_title, travel_pic, country, city, district, latitude, longitude)
        
        return jsonify({'message': 'Journal created successfully!'})
    
    elif request.method == 'GET':
        email = request.args.get('email')
        journals = userData.getJournals(email)
        return jsonify(journals)

@app.route('/api/user', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    if userData.getData(email):
        return jsonify({'message': 'User already exists!'}), 400
    
    # Insert user data into the database
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    userData.insertData(name, email, password_hash)
    return jsonify({'message': 'User created successfully!'})


@app.route("/api/login", methods=["POST"])
def login_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    
    user = userData.getData(email)
    if not user:
        return jsonify({"message": "User not found!"}), 404
    
    # Check if the password is correct
    if bcrypt.check_password_hash(user[2], password):
        return jsonify({"message": "Login successful!"})
    else:
        return jsonify({"message": "Invalid password!"}), 401

@app.route("/api/change_password", methods=["POST"])
def change_password():
    data = request.get_json()
    email = data.get("email")
    new_password = data.get("new_password")
    
    # Hash the new password
    new_password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    
    # Update the password in the database
    userData.changePassword(email, new_password_hash)
    
    return jsonify({"message": "Password changed successfully!"})

@app.route("/api/edit_journal", methods=["POST"])
def edit_journal():
    data = request.get_json()
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
    data = request.get_json()
    rowid = data.get("rowid")
    email = data.get("email")

    # Delete journal data from the database
    userData.deleteJournal(rowid, email)
    
    return jsonify({"message": "Journal deleted successfully!"})

@app.route("/api/delete_user", methods=["POST"])
def delete_user():
    data = request.get_json()
    email = data.get("email")

    # Delete user data from the database
    userData.deleteUser(email)
    
    return jsonify({"message": "User deleted successfully!"})    

if __name__ == '__main__':
    app.run()
 