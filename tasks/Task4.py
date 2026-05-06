import json
import requests
import boto3
import os
from urllib.parse import urlparse

s3 = boto3.client("s3", region_name="us-east-1")
dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

BUCKET_NAME = "music-images-will-2026-a2"
#BUCKET_NAME = "music-images-joshua-2026-a2"
table = dynamodb.Table("music")

with open("2026a2_songs.json", "r", encoding="utf-8") as file:
    data = json.load(file)

for song in data["songs"]:
    image_url = song["img_url"]

    filename = os.path.basename(urlparse(image_url).path)

    response = requests.get(image_url)

    if response.status_code == 200:
        # Upload to S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=filename,
            Body=response.content,
            ContentType="image/jpeg"
        )

        s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{filename}"

        table.update_item(
            Key={
                "title": song["title"],
                "album": song["album"]
            },
            UpdateExpression="SET image_url = :url",
            ExpressionAttributeValues={
                ":url": s3_url
            }
        )

        print(f"Uploaded + updated: {filename}")
    else:
        print(f"Failed: {image_url}")

print("Done")
