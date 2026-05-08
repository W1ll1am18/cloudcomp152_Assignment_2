import boto3
from botocore.exceptions import ClientError

REGION     = "us-east-1"
TABLE_NAME = "music"

dynamodb = boto3.client("dynamodb", region_name=REGION)


def create_music_table():
    try:
        response = dynamodb.create_table(
            TableName=TABLE_NAME,

            # PK: title | SK: album
            KeySchema=[
                {"AttributeName": "title", "KeyType": "HASH"},
                {"AttributeName": "album", "KeyType": "RANGE"},
            ],

            # Declaring attributes used
            AttributeDefinitions=[
                {"AttributeName": "title",  "AttributeType": "S"},
                {"AttributeName": "album",  "AttributeType": "S"},
                {"AttributeName": "artist", "AttributeType": "S"},
            ],

            LocalSecondaryIndexes=[
                {
                    # LSI- query by title + artist
                    "IndexName": "title-artist-lsi",
                    "KeySchema": [
                        {"AttributeName": "title",  "KeyType": "HASH"},
                        {"AttributeName": "artist", "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                },
            ],

            GlobalSecondaryIndexes=[
                {
                    # GSI - query by artist, sorted by title
                    "IndexName": "artist-title-gsi",
                    "KeySchema": [
                        {"AttributeName": "artist", "KeyType": "HASH"},
                        {"AttributeName": "title",  "KeyType": "RANGE"},
                    ],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {
                        "ReadCapacityUnits":  5,
                        "WriteCapacityUnits": 5,
                    },
                }
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
    create_music_table()