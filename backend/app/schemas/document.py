from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    document_id: str
    filename: str
    file_type: str
    file_size_bytes: int
    upload_date: str
    status: str = Field(..., description="'indexed', 'processing', 'failed'")
    chunk_count: int = 0
    error_message: Optional[str] = None


class DocumentUploadResponse(BaseModel):
    message: str
    document_id: str
    filename: str
    chunk_count: int
    status: str


class DocumentListResponse(BaseModel):
    documents: List[DocumentMetadata]
    total_count: int


class DocumentReindexResponse(BaseModel):
    message: str
    document_id: str
    chunk_count: int
    status: str
