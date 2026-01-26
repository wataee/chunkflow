from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    source: str
    category: Optional[str] = "general"
    author: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    custom: Dict[str, Any] = Field(default_factory=dict)


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    chunks_count: int
    status: str
    message: str


class DocumentInfo(BaseModel):
    id: str
    filename: str
    filesize_bytes: int
    chunks_count: int
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
