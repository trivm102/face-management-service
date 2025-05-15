import os
 
API_KEY = os.getenv("API_KEY")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AWS_BUCKET_NAME=os.getenv("AWS_BUCKET_NAME")
AWS_S3_FOLDER=os.getenv("AWS_S3_FOLDER")
 
ENV = os.getenv("ENV", "development")
