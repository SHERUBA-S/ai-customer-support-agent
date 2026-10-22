import os
import shutil
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from app.api.deps import get_current_admin
from app.core.config import settings
from app.core.vector_store import vector_store
from app.services.ingestion import ingestion_service
from app.schemas.document import (
    DocumentMetadata,
    DocumentListResponse,
    DocumentUploadResponse,
    DocumentReindexResponse,
)

router = APIRouter()

ALLOWED_EXTENSIONS = {"pdf", "txt", "md", "markdown"}
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15 MB limit


@router.get("", response_model=DocumentListResponse, summary="List Knowledge Base Documents")
async def list_documents():
    """Retrieve all uploaded documents, processing status, and indexed chunk counts."""
    docs_data = vector_store.list_documents()
    documents = [
        DocumentMetadata(
            document_id=d["document_id"],
            filename=d["filename"],
            file_type=d.get("file_type", "txt"),
            file_size_bytes=d.get("file_size_bytes", 0),
            upload_date=d.get("upload_date", ""),
            status=d.get("status", "unknown"),
            chunk_count=d.get("chunk_count", 0),
            error_message=d.get("error_message"),
        )
        for d in docs_data
    ]
    return DocumentListResponse(documents=documents, total_count=len(documents))


@router.post("/upload", response_model=DocumentUploadResponse, summary="Upload and Ingest Document")
async def upload_document(
    file: UploadFile = File(...),
    _: str = Depends(get_current_admin)
):
    """
    Upload a PDF, TXT, or Markdown document to index into ChromaDB.
    Validates file extension, size, extracts text, chunks, embeds, and stores.
    """
    filename = file.filename or "unknown_file.txt"
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension '.{ext}' is not supported. Please upload PDF, TXT, or MD documents.",
        )

    # Read content to check file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds maximum permitted limit of 15 MB.",
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    # Save to upload directory
    upload_dir = Path(settings.UPLOAD_DIRECTORY)
    os.makedirs(upload_dir, exist_ok=True)
    destination_path = upload_dir / filename

    try:
        with open(destination_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded file to storage: {str(e)}",
        )

    # Process and ingest into vector store
    try:
        doc_record, chunk_count = await ingestion_service.ingest_file(
            file_path=destination_path,
            filename=filename,
        )
        return DocumentUploadResponse(
            message=f"Document '{filename}' successfully processed and indexed into {chunk_count} chunks.",
            document_id=doc_record["document_id"],
            filename=filename,
            chunk_count=chunk_count,
            status="indexed",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to index document '{filename}': {str(e)}",
        )


@router.delete("/{document_id}", summary="Delete Document and Remove Associated Vectors")
async def delete_document(
    document_id: str,
    _: str = Depends(get_current_admin)
):
    """Delete a document, purge all of its vector chunks from ChromaDB, and remove the file."""
    doc = vector_store.get_document(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found.",
        )

    # Delete vectors from ChromaDB
    vector_store.delete_by_document_id(document_id)

    # Remove stored physical file if present
    file_path = doc.get("file_path")
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"[DocumentsAPI] Warning: could not delete file {file_path}: {e}")

    # Remove registry metadata
    vector_store.remove_document_registry(document_id)

    return {
        "message": f"Document '{doc.get('filename')}' and its associated vector chunks were successfully deleted.",
        "document_id": document_id,
    }


@router.post("/{document_id}/reindex", response_model=DocumentReindexResponse, summary="Re-index Document")
async def reindex_document(
    document_id: str,
    _: str = Depends(get_current_admin)
):
    """Re-process and re-generate embeddings and chunks for an existing document."""
    doc = vector_store.get_document(document_id)
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID '{document_id}' not found.",
        )

    file_path = doc.get("file_path")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Physical file for document '{doc.get('filename')}' was not found on disk.",
        )

    try:
        doc_record, chunk_count = await ingestion_service.ingest_file(
            file_path=Path(file_path),
            filename=doc["filename"],
            document_id=document_id,
        )
        return DocumentReindexResponse(
            message=f"Document '{doc['filename']}' successfully re-indexed into {chunk_count} chunks.",
            document_id=document_id,
            chunk_count=chunk_count,
            status="indexed",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Re-indexing failed: {str(e)}",
        )
