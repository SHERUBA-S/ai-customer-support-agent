from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_pipeline import rag_pipeline
from app.api.deps import check_rate_limit

router = APIRouter()


@router.post("/chat", response_model=ChatResponse, summary="Submit Customer Question to RAG Agent")
async def chat_endpoint(
    request: ChatRequest,
    _: None = Depends(check_rate_limit)
):
    """
    Process a customer question:
    1. Query normalization and follow-up contextualization
    2. Vector similarity retrieval against ChromaDB
    3. Similarity threshold filtering
    4. Grounded answer generation using company documents
    5. Returns answer, verifiable source citations, and context status
    """
    try:
        response = await rag_pipeline.run(
            message=request.message,
            conversation_id=request.conversation_id,
            history=request.history,
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while generating the support answer: {str(e)}"
        )
