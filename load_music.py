import json
import boto3

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("music")

with open("2026a2_songs.json", "r", encoding="utf-8") as file:
    data = json.load(file)

songs = data["songs"]

for song in songs:
    item = {
        "title": song["title"],
        "artist": song["artist"],
        "year": song["year"],
        "album": song["album"],
        "image_url": song["img_url"]
    }

    table.put_item(Item=item)
    print(f"Added: {song['title']} - {song['artist']}")

print("Finished loading songs.")
