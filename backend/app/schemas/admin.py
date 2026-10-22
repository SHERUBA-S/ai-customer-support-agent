from typing import List, Optional
from pydantic import BaseModel, Field


class AdminLoginRequest(BaseModel):
    username: str = Field(..., description="Administrator username")
    password: str = Field(..., description="Administrator password")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    expires_in_minutes: int


class AdminStats(BaseModel):
    total_documents: int
    indexed_documents: int
    failed_documents: int
    total_chunks: int
    llm_provider: str
    embedding_provider: str
    system_status: str
