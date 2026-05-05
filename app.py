from flask import Flask, render_template, request, jsonify
import os
import random
import boto3

app = Flask(__name__)
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

@app.route("/")
def index():
    return render_template("main.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login", methods=['POST'])
def loginEvent():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    table = dynamodb.Table('users')
    result = table.get_item(Key={'email': email})
    user = result.get('Item')
    
    if not user or user.get('password') != password:
        return jsonify({'message': 'email or password is invalid'}), 401
    
    return jsonify({'message': 'Login successful'}), 200

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register", methods=['POST'])
def registerEvent():
    data = request.get_json()
    email = data.get('email')
    user_name = data.get('user_name')
    password = data.get('password')
    table = dynamodb.Table('users')
    result = table.get_item(Key={'email': email})
    user = result.get('Item')
    
    if user:
        return jsonify({'message': 'The email already exists'}), 400
        
    table.put_item(Item={
        'email': email,
        'user_name': user_name,
        'password': password
    })
    
    return jsonify({'message': 'Registration successful. Redirecting to login...'}), 200
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))