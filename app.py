# app.py
from flask import Flask, request, redirect, url_for
import boto3
import os
from botocore.exceptions import NoCredentialsError
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
s3 = boto3.client('s3')
ses = boto3.client('ses', region_name='us-east-1')  # e.g., 'us-east-1'

BUCKET_NAME = os.getenv('BUCKET_NAME')
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')

@app.route('/')
def home():
    return '''
        <h1>Upload a picture</h1>
        <form method="post" enctype="multipart/form-data" action="/upload">
            <input type="file" name="file">
            <input type="submit">
        </form>
    '''

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    try:
        s3.upload_fileobj(file, BUCKET_NAME, file.filename)
        send_email(file.filename)
        return 'Upload successful'
    except NoCredentialsError:
        return 'Credentials not available'

def send_email(filename):
    ses.send_email(
        Source=EMAIL_ADDRESS,
        Destination={
            'ToAddresses': [EMAIL_ADDRESS]
        },
        Message={
            'Subject': {
                'Data': 'File Uploaded'
            },
            'Body': {
                'Text': {
                    'Data': f'File {filename} uploaded successfully to {BUCKET_NAME}.'
                }
            }
        }
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
