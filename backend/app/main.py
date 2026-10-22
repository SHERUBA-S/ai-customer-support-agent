import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api import health, chat, documents, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure required directories exist
    os.makedirs(settings.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
    os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)
    print(f"[{settings.PROJECT_NAME}] Server running. LLM: {settings.LLM_PROVIDER}, Embeddings: {settings.EMBEDDING_PROVIDER}")
    yield
    print(f"[{settings.PROJECT_NAME}] Shutting down server.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise-grade RAG AI Customer Support Agent with ChromaDB vector search and source citations.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware - allows any localhost port (5173, 5174, 3000, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS if isinstance(settings.ALLOWED_ORIGINS, list) else ["*"],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:[0-9]+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)},
    )

# Include API Routers
app.include_router(health.router, prefix="/api", tags=["System Health"])
app.include_router(chat.router, prefix="/api", tags=["Customer Chat"])
app.include_router(documents.router, prefix="/api/documents", tags=["Knowledge Base Documents"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin Operations"])


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "AI Customer Support RAG API is operational.",
        "documentation": "/docs",
        "health": "/api/health",
    }
