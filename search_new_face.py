# search_new_face.py

import boto3

from environment import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, AWS_BUCKET_NAME, AWS_S3_FOLDER

def search_face():
    collection_id = "face-collection"
    upload_key = f"{AWS_S3_FOLDER}/new_uploads/ronaldo_jr_2.jpg"

    rekognition = boto3.client("rekognition",
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )

    local_image_path = "ronaldo_jr_2.jpg"
    # Đọc ảnh local thành bytes
    with open(local_image_path, "rb") as image_file:
        image_bytes = image_file.read()

    try:
        response = rekognition.search_faces_by_image(
            CollectionId=collection_id,
            # Image={'S3Object': {'Bucket': AWS_BUCKET_NAME, 'Name': upload_key}},
            Image={'Bytes': image_bytes},
            FaceMatchThreshold=50,  # nên dùng 90–95%
            MaxFaces=10
        )
    except Exception as e:
        print(f"❌ Lỗi khi tìm kiếm: {e}")
        return

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


if __name__ == "__main__":
    search_face()
