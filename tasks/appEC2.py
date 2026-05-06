"""
appEC2.py - EC2 Flask Backend
Run it with: sudo python3 appEC2.py
"""

import boto3
from flask import Flask, request, jsonify, session, redirect, render_template
from flask_cors import CORS
from boto3.dynamodb.conditions import Key, Attr

app = Flask(__name__)
app.secret_key = "a2_secret_key"
CORS(app)

# DynamoDB tables
dynamodb            = boto3.resource("dynamodb", region_name="us-east-1")
login_table         = dynamodb.Table("users")
music_table         = dynamodb.Table("music")
subscriptions_table = dynamodb.Table("subscriptions")


# routes to html
@app.route("/")
def index():
    return redirect("/login")

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/register")
def register_page():
    return render_template("register.html")

@app.route("/main")
def main_page():
    return render_template("main.html")

@app.route("/login", methods=["POST"])
def login():
    try:
        body     = request.get_json()
        email    = body.get("email")
        password = body.get("password")

        if not email or not password:
            return jsonify({"message": "Email and password are required"}), 400

        result = login_table.get_item(Key={"email": email})
        user   = result.get("Item")

        if not user or user.get("password") != password:
            return jsonify({"message": "email or password is invalid"}), 401

        session["email"]     = user["email"]
        session["user_name"] = user["user_name"]

        return jsonify({
            "message":   "Login successful",
            "email":     user["email"],
            "user_name": user["user_name"]
        }), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/register", methods=["POST"])
def register():
    try:
        body      = request.get_json()
        email     = body.get("email")
        user_name = body.get("user_name")
        password  = body.get("password")

        if not email or not user_name or not password:
            return jsonify({"message": "Email, username and password are required"}), 400

        existing = login_table.get_item(Key={"email": email})
        if "Item" in existing:
            return jsonify({"message": "The email already exists"}), 400

        login_table.put_item(Item={
            "email":     email,
            "user_name": user_name,
            "password":  password
        })

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


# music query
@app.route("/query", methods=["GET"])
def query():
    title  = request.args.get("title")
    artist = request.args.get("artist")
    year   = request.args.get("year")
    album  = request.args.get("album")

    if not any([title, artist, year, album]):
        return jsonify({"message": "At least one field is required"}), 400

    try:
        results = []

        if title and artist:
            params = {
                "IndexName":              "title-artist-lsi",
                "KeyConditionExpression": Key("title").eq(title) & Key("artist").eq(artist)
            }
            filters = []
            if year:
                filters.append(Attr("year").eq(year))
            if album:
                filters.append(Attr("album").contains(album))
            if filters:
                params["FilterExpression"] = _combine_filters(filters)
            response = music_table.query(**params)
            results  = response.get("Items", [])

        elif title:
            params = {
                "KeyConditionExpression": Key("title").eq(title)
            }
            filters = []
            if year:
                filters.append(Attr("year").eq(year))
            if album:
                filters.append(Attr("album").contains(album))
            if filters:
                params["FilterExpression"] = _combine_filters(filters)
            response = music_table.query(**params)
            results  = response.get("Items", [])

        elif artist:
            params = {
                "IndexName":              "artist-title-gsi",
                "KeyConditionExpression": Key("artist").eq(artist)
            }
            filters = []
            if year:
                filters.append(Attr("year").eq(year))
            if album:
                filters.append(Attr("album").contains(album))
            if filters:
                params["FilterExpression"] = _combine_filters(filters)
            response = music_table.query(**params)
            results  = response.get("Items", [])

        else:
            filters = []
            if year:
                filters.append(Attr("year").eq(year))
            if album:
                filters.append(Attr("album").contains(album))
            if filters:
                response = music_table.scan(FilterExpression=_combine_filters(filters))
            else:
                response = music_table.scan()
            results = response.get("Items", [])

    except Exception as e:
        return jsonify({"message": str(e)}), 500

    if not results:
        return jsonify({"message": "No result is retrieved. Please query again"}), 404

    return jsonify({"songs": results}), 200


def _combine_filters(filters):
    """Combine multiple filter conditions with AND."""
    result = filters[0]
    for f in filters[1:]:
        result = result & f
    return result


# subscriptions
@app.route("/subscriptions", methods=["GET"])
def get_subscriptions():
    try:
        email = request.args.get("email")
        if not email:
            return jsonify({"message": "Email is required"}), 400

        response = subscriptions_table.query(
            KeyConditionExpression=Key("email").eq(email)
        )
        results = response.get("Items", [])

        if not results:
            return jsonify({"message": "No subscriptions added", "subscriptions": []}), 200

        return jsonify({"subscriptions": results}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/subscribe", methods=["POST"])
def subscribe():
    try:
        body      = request.get_json()
        email     = body.get("email")
        title     = body.get("title")
        album     = body.get("album")
        artist    = body.get("artist")
        year      = body.get("year")
        image_url = body.get("image_url")

        if not email or not title or not album:
            return jsonify({"message": "Email, title and album are required"}), 400

        subscriptions_table.put_item(Item={
            "email":       email,
            "title_album": f"{title}#{album}",
            "title":       title,
            "album":       album,
            "artist":      artist,
            "year":        year,
            "image_url":   image_url
        })

        return jsonify({"message": "Subscribed successfully"}), 201

    except Exception as e:
        return jsonify({"message": str(e)}), 500


@app.route("/unsubscribe", methods=["DELETE"])
def remove_subscription():
    try:
        body  = request.get_json()
        email = body.get("email")
        title = body.get("title")
        album = body.get("album")

        if not email or not title or not album:
            return jsonify({"message": "Email, title and album are required"}), 400

        subscriptions_table.delete_item(Key={
            "email":       email,
            "title_album": f"{title}#{album}"
        })

        return jsonify({"message": "Subscription removed"}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 500

# entry point

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)
