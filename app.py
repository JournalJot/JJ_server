from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import userData

app = Flask(__name__)
cors = CORS(app, origin='*')



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    data = {
        'name': 'John Doe',
        'age': 30,
        'city': 'New York'
    }
    return jsonify(data)

@app.route('/api/user', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    # Insert user data into the database
    userData.insertData(name, email, password)
    
    return jsonify({'message': 'User created successfully!'})

# @app.route('/submit', methods=['POST'])
# def submit():
#     name = request.form['name']
#     return "Hello "+ name + ", your message has been received!"
 