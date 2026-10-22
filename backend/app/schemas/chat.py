from typing import List, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message text content")


class SourceCitation(BaseModel):
    document_name: str = Field(..., description="Source document file name")
    page_number: Optional[int] = Field(None, description="Page number where context was found")
    relevant_excerpt: str = Field(..., description="Direct excerpt from source text")
    relevance_score: float = Field(..., description="Cosine similarity score (0.0 - 1.0)")
    chunk_index: Optional[int] = Field(None, description="Index of the chunk in document")


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000, description="Customer inquiry")
    conversation_id: Optional[str] = Field(None, description="Session conversation ID for multi-turn context")
    history: Optional[List[ChatMessage]] = Field(default_factory=list, description="Recent conversation history")


class ChatResponse(BaseModel):
    answer: str = Field(..., description="AI response grounded in knowledge base")
    sources: List[SourceCitation] = Field(default_factory=list, description="Retrieved source citations")
    conversation_id: str = Field(..., description="Active conversation session ID")
    insufficient_context: bool = Field(False, description="True if no relevant company context was found")
    error: Optional[str] = Field(None, description="Error message if any occurred")
