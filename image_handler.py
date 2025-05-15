import numpy as np
import face_recognition
import faiss
import io
import base64
from typing import List
from constant import *
from request_model.file_request import FileRequest
from model.stored_file import StoredFile
import db as db
import manage_files_s3 as s3

def _insert_new_image(image_bytes, key: str, index_file, filenames_file, db_file, metadata=None) -> dict:
    if not key.strip():
        return {"success": False, "message": "key is empty"}
   
    filenames = s3.read_filenames(filenames_file.name)
   
    if _is_key_name_exists(key, filenames):
        return {"success": False, "message": f"{key}key đã tồn tại"}
    # Đọc ảnh và trích xuất khuôn mặt
    try:
        image = face_recognition.load_image_file(io.BytesIO(image_bytes))
        face_encodings = face_recognition.face_encodings(image)
    except Exception as e:
        return {"success": False, "message": "Đã có lỗi xảy ra"}

    if not face_encodings:
        return {"success": False, "message": "⚠️ Không tìm thấy khuôn mặt trong ảnh."}

    new_embedding = face_encodings[0].astype("float32")

    # Cập nhật FAISS index
    index = faiss.read_index(index_file.name)
    index.add(np.array([new_embedding]))
    faiss.write_index(index, f"{index_file.name}")
    
    # Cập nhật filenames
    filenames.append(key)
    s3.write_filenames(filenames_file.name, filenames)
        
    # ✅ Lưu metadata vào SQLite
    if metadata:
        db.insert_metadata(key, metadata, db_file.name)
    return {"success": True, "message": "Thành công"}

def _is_key_name_exists(filename_to_check: str, filenames) -> bool:
    return filename_to_check in filenames

def insert_images_handler(images: List[FileRequest]):
    filenames_file, index_file, db_file = s3.load_data()
    storedFiles: List[StoredFile] = []
    for img in images:
        img_data = _base64_to_image_bytes(img.data)
        if img_data is None or img.key is None:
            return {"message": "Đã có lỗi xảy ra"}
        else:
            storedFiles.append(StoredFile(img.key, img_data, img.metadata))
    for file in storedFiles:
        dict = _insert_new_image(file.data, file.key, index_file, filenames_file, db_file, file.metadata)
        if dict["success"] == False:
            return dict
    files_to_upload = [
        (filenames_file.name, FILENAME_FILE),
        (index_file.name, FAISS_INDEX_FILE),
        (db_file.name, META_DATA_FILE),
    ]
    if not s3.upload_files_to_s3(files_to_upload):
        s3.clear_temp_data([filenames_file.name, index_file.name, db_file.name])
        return {"success": False, "message": "Lỗi khi upload file"}
    return {"success": True, "message": "Thành công"}

def _base64_to_image_bytes(base64_str: str) -> bytes:
    if not base64_str.strip():
        return None
    try:
        # Giải mã base64
        image_data = base64.b64decode(base64_str)
        return image_data
    except Exception as e:
        print(f"Lỗi khi chuyển base64: {e}")
        return None
    


def delete_images_handler(keys_delete: list[str]) -> dict:
    filenames_file, index_file, db_file = s3.load_data()
    filenames = s3.read_filenames(filenames_file.name)
    index = faiss.read_index(index_file.name)
    
    keys = list(set(keys_delete))
    
    not_found = [key for key in keys if key not in filenames]

    if len(not_found) == len(keys):
        return {"success": False, "message": "Không có key nào tồn tại", "not_found": not_found}

    # Xác định chỉ số các key cần xóa
    indices_to_delete = [filenames.index(key) for key in keys if key in filenames]
    
    # Lấy lại toàn bộ vector trong index (phải rebuild)
    all_embeddings = index.reconstruct_n(0, index.ntotal)

    # Xoá theo index (sort ngược trước khi pop)
    for idx in sorted(indices_to_delete, reverse=True):
        filenames.pop(idx)
        updated_embeddings = np.delete(all_embeddings, idx, axis=0)

    # Rebuild FAISS index
    new_index = faiss.IndexFlatL2(updated_embeddings.shape[1])
    new_index.add(updated_embeddings)
    faiss.write_index(new_index, index_file.name)
    

    # Lưu lại filenames
    s3.write_filenames(filenames_file.name, filenames)

    # Xoá metadata khỏi SQLite
    db.delete_metadata_batch(keys, db_file.name)

    files_to_upload = [
        (filenames_file.name, FILENAME_FILE),
        (index_file.name, FAISS_INDEX_FILE),
        (db_file.name, META_DATA_FILE),
    ]
    if not s3.upload_files_to_s3(files_to_upload):
        s3.clear_temp_data([filenames_file.name, index_file.name, db_file.name])
        return {"success": False, "message": "Lỗi khi upload file"}
    
    if not_found:
        return {"success": True, "message": f"Đã xoá {len(indices_to_delete)}/ {len(keys)} keys", "not_found": not_found}
    
    return {
            "success": True,
            "message": f"Đã xoá {len(indices_to_delete)}/ {len(keys)} keys",
        }
        