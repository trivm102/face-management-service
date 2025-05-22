import boto3
from environment import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, AWS_BUCKET_NAME, AWS_S3_FOLDER

# Tạo client boto3
s3 = boto3.client("s3", 
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY, 
    region_name=AWS_REGION
)

# Initialize Rekognition client
rekognition = boto3.client('rekognition', 
                           aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY, 
    region_name=AWS_REGION)

collection_id = "face-collection"  # Tên tùy ý
bucket_name = AWS_BUCKET_NAME
folder_prefix = f"{AWS_S3_FOLDER}/images/"  # folder chứa ảnh trong S3

# Tạo nếu chưa tồn tại
existing = rekognition.list_collections()['CollectionIds']
if collection_id not in existing:
    rekognition.create_collection(CollectionId=collection_id)
    
response = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_prefix)

for obj in response.get("Contents", []):
    key = obj["Key"]
    if not key.lower().endswith(('.jpg', '.jpeg', '.png')):
        continue

    user_id = key.split('/')[-1].split('.')[0]  # Tùy theo cách đặt tên file

    try:
        rekognition.index_faces(
            CollectionId=collection_id,
            Image={'S3Object': {'Bucket': bucket_name, 'Name': key}},
            ExternalImageId=user_id,
            DetectionAttributes=['DEFAULT']
        )
        print(f"✅ Indexed: {key}")
    except Exception as e:
        print(f"❌ Lỗi khi index {key}: {e}")


#Tìm kiếm ảnh người mới trong collection
upload_key = f"{AWS_S3_FOLDER}/new_uploads/user_temp.jpg"
response = rekognition.search_faces_by_image(
    CollectionId=collection_id,
    Image={'S3Object': {'Bucket': bucket_name, 'Name': upload_key}},
    FaceMatchThreshold=1,
    MaxFaces=10
)

matches = response.get('FaceMatches', [])

if matches:
    print(f"✅ Tìm thấy {len(matches)} ảnh trùng khớp:")
    for i, match in enumerate(matches, start=1):
        similarity = match['Similarity']
        external_id = match['Face'].get('ExternalImageId', 'Không có ID')
        face_id = match['Face']['FaceId']
        print(f"{i}. ExternalImageId: {external_id} | FaceId: {face_id} | Similarity: {similarity:.2f}%")
else:
    print("❌ Không tìm thấy ảnh nào trùng khớp.")
