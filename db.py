import sqlite3
import json
from constant import *

# Tạo kết nối và bảng nếu chưa có
def init_metadata_db(path):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            key TEXT PRIMARY KEY,
            metadata_json TEXT
        )
    """)
    conn.commit()
    conn.close()

# Lưu hoặc cập nhật metadata
def insert_metadata(key: str, metadata: dict, path):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    metadata_json = json.dumps(metadata, ensure_ascii=False)
    cursor.execute("REPLACE INTO metadata (key, metadata_json) VALUES (?, ?)", (key, metadata_json))
    conn.commit()
    conn.close()

# (Tuỳ chọn) Truy xuất metadata theo key
def get_metadata(key: str, path):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("SELECT metadata_json FROM metadata WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()
    return json.loads(row[0]) if row else None

def delete_metadata(key: str, path):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM metadata WHERE key = ?", (key,))
    conn.commit()
    conn.close()

def delete_metadata_batch(keys: list[str], path):
    if not keys:
        return
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.executemany("DELETE FROM metadata WHERE key = ?", [(key,) for key in keys])
    conn.commit()
    conn.close()
