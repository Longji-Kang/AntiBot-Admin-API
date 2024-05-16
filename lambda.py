import json

def handler(event, context):
    body = json.dumps(event['body'])

    return {
        "statusCode": 200,
        "Content-Type": "application/json",
        "body": "{\"event\": body}"
    }