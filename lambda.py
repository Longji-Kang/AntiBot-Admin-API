import json
import os

def handler(event, context):

    params = json.loads(event['body'])

    if params['action'] == 'login':
        if params['username'] == 'admin' and params['password'] == os.environ['pass']:
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": '{"result": "approved"}'
            }
        else:
            return {
                "statusCode": 401,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": '{"result": "invalid"}'
            }
    elif params['action'] == 'upload': 
        a = 2

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": event['body']
    }