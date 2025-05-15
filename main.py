# main.py
from fastapi import FastAPI, File, UploadFile, Body, Header, HTTPException, Depends, Form
import image_search_query as query
from image_handler import insert_images_handler, delete_images_handler
import io
from typing import List
from contextlib import asynccontextmanager
from request_model.file_request import FileRequest
from request_model.keys_request import KeysRequest
from environment import ENV, API_KEY
import manage_files_s3 as s3


if not API_KEY:
    raise Exception("Missing API_KEY environment variable!")

if ENV == "production":
    print("🚀 Đang chạy ở môi trường production")
else:
    print(f"⚙️ Đang chạy ở môi trường {ENV}")

def initialize():
    s3.check_files_on_s3()
    print("✅ initialize successful.")

# ⚙️ Lifespan event
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 FastAPI khởi động...")
    initialize()
    print("📂 Loading dữ liệu...")
    yield

app = FastAPI(lifespan=lifespan)


def verify_api_key(access_token: str = Header(...)):
    if access_token != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")


@app.post("/search")
async def search_face(file: UploadFile = File(...),
                      top_k: int = Form(5, description="Số lượng ảnh giống nhất cần trả về"), 
                      _: str = Depends(verify_api_key)):
    image_bytes = await file.read()
    result = query.search_face(io.BytesIO(image_bytes))
    return result

@app.post("/insert-images",)
async def insert_images(images: List[FileRequest], _: str = Depends(verify_api_key)):
    result = insert_images_handler(images)
    return result

@app.delete("/delete-images")
async def delete_images(request: KeysRequest= Body(...), _: str = Depends(verify_api_key)):
    keys = request.keys
    result = delete_images_handler(keys)
    return result