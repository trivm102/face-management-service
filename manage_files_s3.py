import boto3
import faiss
from botocore.exceptions import NoCredentialsError, ClientError
import tempfile
from constant import *
from environment import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, AWS_BUCKET_NAME, AWS_S3_FOLDER
import os
import db as db

# Tạo client boto3
s3 = boto3.client("s3", 
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY, 
    region_name=AWS_REGION
)

def check_files_on_s3():
    filename_path = None
    index_path = None
    db_path = None
    temp_dir = tempfile.gettempdir()
    if load_filenames_from_s3() is None:
        filename_path = os.path.join(temp_dir, FILENAME_FILE)
        with open(filename_path, "w") as f:
            pass
        
    if load_faiss_index_from_s3() is None:
        index_path = os.path.join(temp_dir, FAISS_INDEX_FILE)
        indexFile = faiss.IndexFlatL2(128)  # FAISS dùng vector 128 chiều
        faiss.write_index(indexFile, index_path)
        
    if load_sqlite_db_from_s3() is None:
        db_path = os.path.join(temp_dir, META_DATA_FILE)
        db.init_metadata_db(db_path)
        
    if all([filename_path, index_path, db_path]):
    
        files_to_upload = [
            (filename_path, FILENAME_FILE),
            (index_path, FAISS_INDEX_FILE),
            (db_path, META_DATA_FILE),
        ]

        for local_path, s3_filename in files_to_upload:
            upload_file_to_s3(local_path, s3_filename)
        clear_temp_data([filename_path, index_path, db_path])

def upload_files_to_s3(files_to_upload: list[tuple[str, str]]):

    for local_path, s3_filename in files_to_upload:
        result = upload_file_to_s3(local_path, s3_filename)
        if not result:
            return False
    return True

def upload_file_to_s3(local_path: str, s3_filename: str) -> bool:
    if not local_path:
        print(f"⚠️ Đường dẫn file rỗng, bỏ qua upload {s3_filename}")
        return False
    try:
        s3.upload_file(local_path, AWS_BUCKET_NAME, f"{AWS_S3_FOLDER}/{s3_filename}")
        print(f"✅ Upload thành công: {local_path} → s3://{AWS_BUCKET_NAME}/{AWS_S3_FOLDER}/{s3_filename}")
        return True
    except (FileNotFoundError, NoCredentialsError, ClientError) as e:
        print(f"❌ Lỗi upload {local_path}: {e}")
        return False

def download_file_from_s3(key: str) -> bytes:
    try:
        response = s3.get_object(Bucket=AWS_BUCKET_NAME, Key=key)
        return response['Body'].read()
    except ClientError as e:
        print(f"⚠️ Không thể tải file {key} từ S3: {e}")
        return None

def load_filenames_from_s3():
    data = download_file_from_s3(f"{AWS_S3_FOLDER}/{FILENAME_FILE}")
    if data is None:
        return None
    if data or len(data) >= 0:
        # Ghi vào file tạm và đọc lại
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(data)
            tmp.flush()
            return tmp
    return None

def read_filenames(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]
    return ""

def write_filenames(path, new_data):
    with open(path, "w") as f:
        f.writelines([name + "\n" for name in new_data])
        return True
    return False

def load_faiss_index_from_s3():
    data = download_file_from_s3(f"{AWS_S3_FOLDER}/{FAISS_INDEX_FILE}")
    if data:
        try:
            # Ghi vào file tạm và đọc lại
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(data)
                tmp.flush()
                return tmp
        except Exception as e:
            print(f"❌ Lỗi khi đọc FAISS index từ file tạm: {e}")
    return None

def load_sqlite_db_from_s3():
    data = download_file_from_s3(f"{AWS_S3_FOLDER}/{META_DATA_FILE}")
    if data:
       with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(data)
            tmp.flush()
            return tmp
    return None

def clear_temp_data(files: list[str]):
    for file_path in files:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"🗑️ Đã xóa: {file_path}")
            except Exception as e:
                print(f"⚠️ Không thể xóa {file_path}: {e}")
        else:
            print(f"⚠️ File không tồn tại: {file_path}")

def load_data():
    filenames = load_filenames_from_s3()
    index = load_faiss_index_from_s3()
    db = load_sqlite_db_from_s3()
   
    return filenames, index, db
