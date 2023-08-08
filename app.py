from flask import Flask, render_template, request, redirect
import boto3
import os
import uuid

app = Flask(__name__)

S3_BUCKET = 'bucketforfiles123'
S3_REGION = 'us-east-2'
LAMBDA_FUNCTION_NAME = 'emailservice'

s3_client = boto3.client('s3', region_name=S3_REGION)
lambda_client = boto3.client('lambda', region_name=S3_REGION)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    uploaded_file = request.files['file']
    emails = request.form['emails'].split(',')
    file_name = str(uuid.uuid4()) + os.path.splitext(uploaded_file.filename)[1]
    
    s3_client.upload_fileobj(
        uploaded_file, 
        S3_BUCKET, 
        file_name,
        ExtraArgs={'ACL': 'public-read'}
    )
    
    file_link = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file_name}"
    
    lambda_response = lambda_client.invoke(
        FunctionName=LAMBDA_FUNCTION_NAME,
        InvocationType="RequestResponse",
        Payload=json.dumps({
            'file_link': file_link,
            'file_name': file_name,
            'user_email': 'faixifk3@gmail.com',
            'emails': emails
        })
    )
    
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
