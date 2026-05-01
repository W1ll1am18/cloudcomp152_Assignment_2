import json
import boto3

from botocore.exceptions import ClientError
 
REGION     = "us-east-1"
TABLE_NAME = "music"
JSON_FILE  = "2026a2_songs.json"
 
dynamodb = boto3.resource("dynamodb", region_name=REGION)
 
 
def load_songs(json_path: str) -> None:
    table = dynamodb.Table(TABLE_NAME)
 
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
 
    songs = data["songs"]
    print(f"Loaded {len(songs)} songs from '{json_path}'.")
 
    success_count = 0
    error_count   = 0

    with table.batch_writer() as batch:
        for song in songs:
            title     = song["title"]
            artist    = song["artist"]
            year      = song["year"]
            album     = song["album"]
            image_url = song["img_url"]
 
            
            title_album = f"{title}#{album}"
 
            try:
                batch.put_item(
                    Item={
                        "artist":      artist,       
                        "title_album": title_album,  
                        "title":       title,    
                        "year":        year,
                        "album":       album,
                        "image_url":   image_url,
                    }
                )
                success_count += 1
 
            except ClientError as e:
                print(f"  ERROR writing '{title}' by '{artist}': "
                      f"{e.response['Error']['Message']}")
                error_count += 1
 
    print(f"\nImport complete.")
    print(f"  Successfully queued : {success_count} songs")
    print(f"  Errors              : {error_count} songs")
 
 
def verify_load(expected_count: int) -> None:
    """Scan the table and confirm item count matches the source JSON."""
    table = dynamodb.Table(TABLE_NAME)
    response = table.scan(Select="COUNT")
    actual = response["Count"]
 
    # Handle results for large tables
    while "LastEvaluatedKey" in response:
        response = table.scan(
            Select="COUNT",
            ExclusiveStartKey=response["LastEvaluatedKey"]
        )
        actual += response["Count"]
 
    print(f"\nVerification: {actual} items in '{TABLE_NAME}' (expected {expected_count}).")
    if actual == expected_count:
        print("All songs loaded successfully - lossless import confirmed.")
    else:
        print(f"Mismatch! {expected_count - actual} songs may be missing.")
 
 
if __name__ == "__main__":
    load_songs(JSON_FILE)
 
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        expected = len(json.load(f)["songs"])

    verify_load(expected)
