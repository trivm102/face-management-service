from typing import Optional, Dict, Any
class StoredFile:
    def __init__(self, key: str, data: bytes, metadata: Dict[str, Any] = None):
        self.key = key
        self.data = data
        self.metadata = metadata
