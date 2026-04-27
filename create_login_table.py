#Run Task1 instead of this seperately
import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

def create_login_table():
    try:
        table = dynamodb.create_table(
            TableName='users',
            KeySchema=[
                {'AttributeName': 'email', 'KeyType': 'HASH'}, #Partition Key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'email', 'AttributeType': 'S'},
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        
        table.wait_until_exists()
        print(f"Success. Table status: {table.table_status}")
        
    except Exception as e:
        print(f"Unable to create table: {e}")