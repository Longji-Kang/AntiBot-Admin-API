import json
import os
import base64
import boto3
import time

def upload_file(file_dir, target_file):
    s3_client = boto3.client('s3')
    s3_client.upload_file(file_dir, os.environ['s3_bucket'], f"{os.environ['s3_folder']}/{target_file}")

def add_to_dynamo(version, url):
    dynamo = boto3.resource('dynamodb')
    table = dynamo.Table(os.environ['dynamo_table'])

    table.put_item(
        Item = {
            "Id" : 1,
            "Version": version,
            "Url": url
        }
    )

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
        file_content = str(base64.b64decode(params['content']), encoding='ascii')
        epoch        = int(time.time())
        file_name    = f'{epoch}-definition.pkl'
        file_dir     = f"/mnt/lambda/{file_name}"

        file = open(file_dir, 'w')
        file.write(file_content)
        file.close()
        upload_file(file_dir, file_name)
        
        file_url = os.environ['url_base'] + file_name

        add_to_dynamo(str(epoch), file_url)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": '{"result": "success"}'
        }