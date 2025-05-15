import numpy as np
import face_recognition
import manage_files_s3 as s3
import faiss
import db

def search_face(query_file, top_k=10):
    try:
        query_image = face_recognition.load_image_file(query_file)
        query_faces = face_recognition.face_encodings(query_image)
        
        filenames_file = s3.load_filenames_from_s3()
        filenames = s3.read_filenames(filenames_file.name)
        
        faiss_index_file = s3.load_faiss_index_from_s3()
        index = faiss.read_index(faiss_index_file.name)
        
        db_file = s3.load_sqlite_db_from_s3()
    except Exception as e:
        print(f"❌ Lỗi khi load ảnh query: {e}")
        return {"success": False, "message": "Lỗi khi load dữ liệu."}

    if not query_faces:
        print("❌ Không tìm thấy khuôn mặt trong ảnh truy vấn.")
        return {"success": False, "message": "Không tìm thấy khuôn mặt trong ảnh truy vấn."}
    
    if index.ntotal == 0 or len(filenames) == 0:
        return {"success": False, "message": "Không tìm thấy dữ liệu"}
    if index.ntotal < top_k:
        top_k = index.ntotal
    
    query_embedding = query_faces[0].astype('float32')
    distances, indices = index.search(np.array([query_embedding]), top_k)

    results = []
    for i, idx in enumerate(indices[0]):
        distance = distances[0][i]
        diff_percent = distance * 100
        print(f"diff_percent {diff_percent}")
        similarity_percent = 100 - diff_percent
        print(f"similarity_percent {similarity_percent}")
        key = filenames[idx]
        metadata = db.get_metadata(key, db_file.name)
        
        results.append({
            "rank": i + 1,
            "key": key,
            "metadata": metadata,
            "similarity": round(float(similarity_percent), 2)
        })
    s3.clear_temp_data([filenames_file.name, faiss_index_file.name, db_file.name])
    return {"success": True, "results": results}

