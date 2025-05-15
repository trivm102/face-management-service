import os
 
API_KEY = os.getenv("API_KEY")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AWS_BUCKET_NAME="mysearchface"
AWS_S3_FOLDER="uploads"
 
ENV = os.getenv("ENV", "development")
