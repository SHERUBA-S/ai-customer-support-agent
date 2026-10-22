from fastapi import APIRouter
from app.core.config import settings
from app.core.vector_store import vector_store

router = APIRouter()


@router.get("/health", summary="System Health and Status Check")
async def health_check():
    """
    Returns application status, vector database statistics, and active LLM configuration.
    """
    total_chunks = vector_store.count_total_chunks()
    docs = vector_store.list_documents()
    indexed_docs = sum(1 for d in docs if d.get("status") == "indexed")

    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "llm_provider": settings.LLM_PROVIDER,
        "embedding_provider": settings.EMBEDDING_PROVIDER,
        "total_documents": len(docs),
        "indexed_documents": indexed_docs,
        "total_indexed_chunks": total_chunks,
        "vector_store": "ChromaDB (Persistent)",
    }
