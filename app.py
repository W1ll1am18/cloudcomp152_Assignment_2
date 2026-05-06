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
    try:
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

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register", methods=['POST'])
def registerEvent():
    try:
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

    except Exception as e:
        return jsonify({'message': str(e)}), 500


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
        
    artist = request.args.get('artist')
    song   = request.args.get('song')
    album  = request.args.get('album')
    year   = request.args.get('year')
        
    if not any([song, artist, year, album]):
        return jsonify({'message': 'At least one field is required'}), 400
    
    table = dynamodb.Table('music')
    results = []
    
    try:
        #If song and artist exists use LSI table
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
        #If song not artists exists use Main table
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
        #If artist exists use GSI table
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
        #Else scan non key fields
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

@app.route("/subscriptions", methods=['GET'])
def getAllSubscriptions():   
    try:
        email = request.args.get('email')
        results = []
        table = dynamodb.Table('subscriptions')
        
        response = table.query(KeyConditionExpression=Key('email').eq(email))
        results = response.get('Items', [])

        if not results:
            return jsonify({'message': 'No subcriptions added'}), 200
        
        return jsonify({'Subscriptions': results}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route("/subscribe", methods=['POST'])
def subscribe():
    try:
        data = request.get_json()
        email = data.get('email')
        title = data.get('title')
        album = data.get('album')
        artist = data.get('artist')
        year = data.get('year')
        image_url = data.get('image_url')

        if not email or not title or not album:
            return jsonify({'message': 'Email, title and album are required'}), 400

        table = dynamodb.Table('subscriptions')
        table.put_item(Item={
            'email': email,
            'title_album': f"{title}#{album}",
            'title': title,
            'album': album,
            'artist': artist,
            'year': year,
            'image_url': image_url
        })
        return jsonify({'message': 'Subscribed successfully'}), 201

    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@app.route("/unsubscribe", methods=['DELETE'])
def removeSubcription():
    try:
        data  = request.get_json()
        email = data.get('email')
        title = data.get('title')
        album = data.get('album')

        if not email or not title or not album:
            return jsonify({'message': 'Email, title and album are required'}), 400

        table = dynamodb.Table('subscriptions')
        table.delete_item(Key={
            'email':       email,
            'title_album': f"{title}#{album}"
        })
        return jsonify({'message': 'Subscription removed'}), 200

    except Exception as e:
        return jsonify({'message': str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)