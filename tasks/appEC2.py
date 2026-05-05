"""
appEC2.py - EC2 Flask Backend
Run with: python appEC2.py
"""

import boto3
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from boto3.dynamodb.conditions import Key, Attr

app = Flask(__name__)
app.secret_key = "a2_secret_key"
CORS(app)

# Dynamodb tables
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
login_table         = dynamodb.Table("users")
music_table         = dynamodb.Table("music")
subscriptions_table = dynamodb.Table("subscriptions")

@app.route("/login", methods=["POST"])
def login():
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


@app.route("/register", methods=["POST"])
def register():
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


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


# music query
@app.route("/music", methods=["GET"])
def query_music():
    title  = request.args.get("title")
    artist = request.args.get("artist")
    year   = request.args.get("year")
    album  = request.args.get("album")

    if not any([title, artist, year, album]):
        return jsonify({"message": "At least one query field is required"}), 400

    filter_parts = []
    expr_values  = {}
    expr_names   = {}

    if title:
        filter_parts.append("#t = :title")
        expr_names["#t"]      = "title"
        expr_values[":title"] = title

    if artist:
        filter_parts.append("#a = :artist")
        expr_names["#a"]       = "artist"
        expr_values[":artist"] = artist

    if year:
        filter_parts.append("#y = :year")
        expr_names["#y"]     = "year"
        expr_values[":year"] = year

    if album:
        filter_parts.append("#al = :album")
        expr_names["#al"]     = "album"
        expr_values[":album"] = album

    filter_expression = " AND ".join(filter_parts)

    if artist:
        kwargs = {
            "IndexName":                 "artist-title-gsi",
            "KeyConditionExpression":    Key("artist").eq(artist),
            "ExpressionAttributeNames":  {k: v for k, v in expr_names.items()},
            "ExpressionAttributeValues": {k: v for k, v in expr_values.items()},
        }
        remaining = [p for p in filter_parts if "#a" not in p]
        if remaining:
            kwargs["FilterExpression"] = " AND ".join(remaining)

        response = music_table.query(**kwargs)

    else:
        response = music_table.scan(
            FilterExpression=filter_expression,
            ExpressionAttributeNames= {k: v for k, v in expr_names.items()},
            ExpressionAttributeValues={k: v for k, v in expr_values.items()},
        )

    items = response.get("Items", [])

    if not items:
        return jsonify({"message": "No result is retrieved. Please query again", "songs": []}), 200

    return jsonify({"songs": items}), 200

# subscriptionss
@app.route("/subscriptions", methods=["GET"])
def get_subscriptions():
    email = request.args.get("email")
    if not email:
        return jsonify({"message": "Email is required"}), 400

    response = subscriptions_table.scan(
        FilterExpression=Attr("email").eq(email)
    )

    return jsonify({"subscriptions": response.get("Items", [])}), 200


@app.route("/subscribe", methods=["POST"])
def subscribe():
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


@app.route("/subscribe", methods=["DELETE"])
def remove_subscription():
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


# entry point
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=False)
