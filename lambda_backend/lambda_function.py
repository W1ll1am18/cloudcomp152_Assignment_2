import json
import boto3

from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')

LOGIN_TABLE = "users"
MUSIC_TABLE = "music"
SUBSCRIPTIONS_TABLE = "subscriptions"

login_table = dynamodb.Table(LOGIN_TABLE)
music_table = dynamodb.Table(MUSIC_TABLE)
subscriptions_table = dynamodb.Table(SUBSCRIPTIONS_TABLE)

def make_response(status_code, body):
    return {
        'statusCode': status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization"
        },
        'body': json.dumps(body)
    }

def lambda_handler(event, context):
    method = event['httpMethod']
    path = event['path']

    if method == 'OPTIONS':
        return make_response(200, {"message": "CORS OK"})
    
    if path == '/login' and method == 'POST':
        return login(event)
    
    if path == "/register" and method == 'POST':
        return register(event)
    
    if path == "/music" and method == 'GET':
        return query_music(event)
    
    if path == "/subscriptions" and method == "GET":
        return get_subscriptions(event)
    
    if path == "/subscribe" and method == 'POST':
        return subscribe(event)
    
    if path == "/subscribe" and method == 'DELETE':
        return remove_subscription(event)
    
    return make_response(404, {"message": "Not Found"})

def login(event):
    body = json.loads(event.get("body", "{}"))

    email = body.get("email")
    password = body.get("password")

    if not email or not password:
        return make_response(400, {"message": "Email and password are required"})

    result = login_table.get_item(Key={"email": email})
    user = result.get("Item")

    if not user or user.get("password") != password:
        return make_response(401, {"message": "email or password is invalid"})

    return make_response(200, {
        "message": "Login successful",
        "email": user.get("email"),
        "user_name": user.get("user_name")
    })

def register(event):
    return make_response(200, {"message": "Register endpoint"})

def query_music(event):
    return make_response(200, {"message": "music query endpoint working"})


def get_subscriptions(event):
    return make_response(200, {"message": "subscriptions endpoint working"})


def subscribe(event):
    return make_response(200, {"message": "subscribe endpoint working"})


def remove_subscription(event):
    return make_response(200, {"message": "remove subscription endpoint working"})
    
