from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_current_admin
from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.core.vector_store import vector_store
from app.schemas.admin import AdminLoginRequest, TokenResponse, AdminStats

router = APIRouter()


@router.post("/login", response_model=TokenResponse, summary="Admin Login and JWT Token Generation")
async def admin_login(request: AdminLoginRequest):
    """
    Authenticate administrator credentials and return a Bearer JWT token.
    """
    is_user_valid = (request.username == settings.ADMIN_USERNAME)
    is_pass_valid = verify_password(request.password, settings.ADMIN_PASSWORD)

    if not is_user_valid or not is_pass_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect admin username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(
        subject=request.username,
        expires_delta=access_token_expires
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        username=request.username,
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )


@router.get("/stats", response_model=AdminStats, summary="Knowledge Base Analytics and Status")
async def admin_stats(_: str = Depends(get_current_admin)):
    """
    Retrieve real-time statistics regarding indexed documents, vector chunks, and system health.
    """
    docs = vector_store.list_documents()
    total_docs = len(docs)
    indexed_docs = sum(1 for d in docs if d.get("status") == "indexed")
    failed_docs = sum(1 for d in docs if d.get("status") == "failed")
    total_chunks = vector_store.count_total_chunks()

    return AdminStats(
        total_documents=total_docs,
        indexed_documents=indexed_docs,
        failed_documents=failed_docs,
        total_chunks=total_chunks,
        llm_provider=settings.LLM_PROVIDER,
        embedding_provider=settings.EMBEDDING_PROVIDER,
        system_status="operational",
    )
