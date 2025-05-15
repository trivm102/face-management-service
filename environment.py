import os
 
API_KEY = "75ea30fa79092d17fe35367a5c052b0b279ccde3b83aba5ac2387ac4ebc26eff"
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION")
AWS_BUCKET_NAME="mysearchface"
AWS_S3_FOLDER="uploads"
 
ENV = os.getenv("ENV", "development")
