import json
import os
import base64
import boto3
import time
from zipfile import ZipFile

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

def sanitizeFile(file: str):
    content_64 = file.split(',')[1]
    content = base64.b64decode(content_64)    

    return content

def handler(event, context):

    params = json.loads(event['body'])

    if params['action'] == 'login':
        if params['username'] == 'admin' and params['password'] == os.environ['pass']:
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": '{"result": "approved"}'
            }
        else:
            return {
                "statusCode": 401,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": '{"result": "invalid"}'
            }
    elif params['action'] == 'upload': 
        # ZIP File
        file_content = str(base64.b64decode(params['content']), encoding='ascii')
        file_content_sanitized = sanitizeFile(file_content)
        file_dir     = f"/mnt/lambda/"

        temp_file = "temp.zip"

        zip_file = open(f'{file_dir}/{temp_file}', "wb")
        zip_file.write(file_content_sanitized)
        zip_file.close()

        with ZipFile(f'{file_dir}/{temp_file}') as zip:
            zip.extractall(f'{file_dir}/')

        epoch        = int(time.time())
        file_name    = f'{epoch}-definition.pkl'

        upload_file(f'{file_dir}/model.pkl', file_name)
        
        file_url = os.environ['url_base'] + file_name

        add_to_dynamo(str(epoch), file_url)

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": '{"result": "success"}'
        }