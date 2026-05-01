#Run Task1 instead of this seperately
import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

def load_users():
    table = dynamodb.Table('users')
    
    users = [
        {'email': 's4095329@student.rmit.edu.au', 'user_name': 'William', 'password': 'William1'},
        {'email': 's3939929@student.rmit.edu.au', 'user_name': 'Joshua', 'password': 'Joshua2'},
        {'email': 's4161629@student.rmit.edu.au', 'user_name': 'YuHern', 'password': 'YuHern3'},
        {'email': 'dummy1@student.rmit.edu.au', 'user_name': 'Dummy1', 'password': 'Dummy1'},
        {'email': 'dummy2@student.rmit.edu.au', 'user_name': 'Dummy2', 'password': 'Dummy2'},
        {'email': 'dummy3@student.rmit.edu.au', 'user_name': 'Dummy3', 'password': 'Dummy3'},
        {'email': 'dummy4@student.rmit.edu.au', 'user_name': 'Dummy4', 'password': 'Dummy4'},
        {'email': 'dummy5@student.rmit.edu.au', 'user_name': 'Dummy5', 'password': 'Dummy5'},
        {'email': 'dummy6@student.rmit.edu.au', 'user_name': 'Dummy6', 'password': 'Dummy6'},
        {'email': 'dummy7@student.rmit.edu.au', 'user_name': 'Dummy7', 'password': 'Dummy7'},        
    ]
    
    for user in users:
        table.put_item(Item=user)
        print(f"Added user: {user['email']}")