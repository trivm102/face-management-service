# index_all_faces_once.py

import boto3

from environment import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, AWS_BUCKET_NAME, AWS_S3_FOLDER

def index_faces_once():
    collection_id = "face-collection"
    folder_prefix = f"{AWS_S3_FOLDER}/images/"

    s3 = boto3.client("s3",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )

    rekognition = boto3.client("rekognition",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )

    # Tạo collection nếu chưa có
    existing_collections = rekognition.list_collections().get('CollectionIds', [])
    if collection_id not in existing_collections:
        rekognition.create_collection(CollectionId=collection_id)
        print(f"🆕 Tạo mới collection: {collection_id}")

    # Lấy danh sách ExternalImageId đã index
    existing_ids = set()
    next_token = None
    while True:
        if next_token:
            response = rekognition.list_faces(CollectionId=collection_id, NextToken=next_token)
        else:
            response = rekognition.list_faces(CollectionId=collection_id)

        for face in response.get('Faces', []):
            existing_ids.add(face.get('ExternalImageId'))

        next_token = response.get('NextToken')
        if not next_token:
            break

    print(f"🔍 Đã có {len(existing_ids)} ảnh đã index.")

    # Lấy danh sách ảnh trong S3
    response = s3.list_objects_v2(Bucket=AWS_BUCKET_NAME, Prefix=folder_prefix)
    for obj in response.get("Contents", []):
        key = obj["Key"]
        if not key.lower().endswith(('.jpg', '.jpeg', '.png')):
            continue

        user_id = key.split('/')[-1].split('.')[0]

        if user_id in existing_ids:
            print(f"⏩ Bỏ qua (đã index): {key}")
            continue

        try:
            rekognition.index_faces(
                CollectionId=collection_id,
                Image={'S3Object': {'Bucket': AWS_BUCKET_NAME, 'Name': key}},
                ExternalImageId=user_id,
                DetectionAttributes=['DEFAULT']
            )
            print(f"✅ Indexed: {key}")
        except Exception as e:
            print(f"❌ Lỗi khi index {key}: {e}")


if __name__ == "__main__":
    index_faces_once()