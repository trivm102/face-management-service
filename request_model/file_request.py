from typing import Optional, Dict, Any
from pydantic import BaseModel

class FileRequest(BaseModel):
    key: str
    data: str
    metadata: Optional[Dict[str, Any]] = None