"""
create_subscriptions_table.py
Creates the 'subscriptions' DynamoDB table.
"""

import boto3
from botocore.exceptions import ClientError

REGION     = "us-east-1"
TABLE_NAME = "subscriptions"

dynamodb = boto3.client("dynamodb", region_name=REGION)


def create_subscriptions_table():
    try:
        response = dynamodb.create_table(
            TableName=TABLE_NAME,

            # PK: email
            # SK: title_album
            KeySchema=[
                {"AttributeName": "email",       "KeyType": "HASH"},
                {"AttributeName": "title_album", "KeyType": "RANGE"},
            ],

            AttributeDefinitions=[
                {"AttributeName": "email",       "AttributeType": "S"},
                {"AttributeName": "title_album", "AttributeType": "S"},
            ],

            BillingMode="PROVISIONED",
            ProvisionedThroughput={
                "ReadCapacityUnits":  5,
                "WriteCapacityUnits": 5,
            },
        )

        print(f"Table '{TABLE_NAME}' creation initiated.")
        print(f"Status: {response['TableDescription']['TableStatus']}")


      
        waiter = dynamodb.get_waiter("table_exists")
        print("Waiting for table to become ACTIVE...")
        waiter.wait(TableName=TABLE_NAME)
        print(f"Table '{TABLE_NAME}' is now ACTIVE and ready.")

    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code == "ResourceInUseException":
            print(f"Table '{TABLE_NAME}' already exists - skipping creation.")
        else:
            raise


if __name__ == "__main__":
    create_subscriptions_table()
