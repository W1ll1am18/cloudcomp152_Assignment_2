from flask import Flask, render_template, request, jsonify, redirect
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr

app = Flask(__name__)
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

@app.route("/")
def index():
    return redirect('/login')

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
    
    return jsonify({
        'message': 'Login successful',
        'email': user['email'],
        'user_name': user['user_name']
    }), 200

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

@app.route("/main")
def main():
    return render_template("main.html")

@app.route("/query", methods=['GET'])
def query():
    def filterHelper(filters):
        filter_conditions = filters[0]
        for f in filters[1:]:
            filter_conditions = filter_conditions & f
        return filter_conditions
        
    # read from URL params instead of JSON body
    artist = request.args.get('artist')
    song   = request.args.get('song')
    album  = request.args.get('album')
    year   = request.args.get('year')
        
    if not any([song, artist, year, album]):
        return jsonify({'message': 'At least one field is required'}), 400
    
    table = dynamodb.Table('music')
    results = []
    
    try:
        if song and artist:
            params = {
                "IndexName": "title-artist-lsi",
                'KeyConditionExpression': Key('title').eq(song) & Key('artist').eq(artist)
            }
            filters = []
            if year:
                filters.append(Attr('year').eq(year))
            if album:
                filters.append(Attr('album').contains(album))
            if filters:
                params['FilterExpression'] = filterHelper(filters)
            response = table.query(**params)
            results = response.get('Items', [])
        
        elif song:
            params = {
                'KeyConditionExpression': Key('title').eq(song)
            }
            filters = []
            if year:
                filters.append(Attr('year').eq(year))
            if album:
                filters.append(Attr('album').contains(album))
            if filters:
                params['FilterExpression'] = filterHelper(filters)
            response = table.query(**params)
            results = response.get('Items', [])
        
        elif artist:
            params = {
                "IndexName": "artist-title-gsi",
                'KeyConditionExpression': Key('artist').eq(artist)
            }
            filters = []
            if year:
                filters.append(Attr('year').eq(year))
            if album:
                filters.append(Attr('album').contains(album))
            if filters:
                params['FilterExpression'] = filterHelper(filters)
            response = table.query(**params)
            results = response.get('Items', [])
            
        else:
            filters = []
            if year:
                filters.append(Attr('year').eq(year))
            if album:
                filters.append(Attr('album').contains(album))
            if filters:
                response = table.scan(FilterExpression=filterHelper(filters))
            else:
                response = table.scan()
            results = response.get('Items', [])            

    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
    if not results:
        return jsonify({'message': 'No result is retrieved. Please query again'}), 404
     
    return jsonify({'songs': results}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)