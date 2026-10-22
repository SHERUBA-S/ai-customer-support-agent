import os
import uuid
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader

from app.core.config import settings
from app.core.vector_store import vector_store
from app.services.embeddings import embedding_service


class IngestionService:
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP

    def compute_file_hash(self, content_bytes: bytes) -> str:
        """Compute SHA256 hash of file content for deduplication."""
        return hashlib.sha256(content_bytes).hexdigest()

    def extract_text_from_file(self, file_path: Path, filename: str) -> List[Dict[str, Any]]:
        """
        Extract text from file.
        Returns a list of page/section dicts: [{'page_number': int, 'text': str}]
        """
        ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
        pages_content: List[Dict[str, Any]] = []

        if ext == "pdf":
            try:
                reader = PdfReader(str(file_path))
                for page_idx, page in enumerate(reader.pages):
                    page_text = page.extract_text() or ""
                    # Clean out excess nulls or strange chars
                    page_text = page_text.replace("\x00", "").strip()
                    if page_text:
                        pages_content.append({
                            "page_number": page_idx + 1,
                            "text": page_text
                        })
            except Exception as e:
                raise ValueError(f"Failed to extract text from PDF '{filename}': {str(e)}")

        elif ext in ["txt", "md", "markdown"]:
            # Try utf-8 first, fallback to latin-1
            text = ""
            for encoding in ["utf-8", "utf-8-sig", "latin-1"]:
                try:
                    with open(file_path, "r", encoding=encoding) as f:
                        text = f.read()
                    break
                except UnicodeDecodeError:
                    continue
            
            text = text.replace("\x00", "").strip()
            if text:
                pages_content.append({
                    "page_number": 1,
                    "text": text
                })
        else:
            raise ValueError(f"Unsupported file format: '.{ext}'. Supported formats are: PDF, TXT, MD.")

        if not pages_content:
            raise ValueError(f"No extractable text found in file '{filename}'.")

        return pages_content

    def chunk_text(
        self,
        pages_content: List[Dict[str, Any]],
        document_id: str,
        filename: str
    ) -> List[Dict[str, Any]]:
        """
        Split document text into overlapping chunks while preserving sentence boundaries and metadata.
        """
        chunks: List[Dict[str, Any]] = []
        chunk_idx = 0

        for page in pages_content:
            page_num = page["page_number"]
            text = page["text"]

            if len(text) <= self.chunk_size:
                chunk_id = f"{document_id}_c{chunk_idx}"
                chunks.append({
                    "chunk_id": chunk_id,
                    "document_id": document_id,
                    "filename": filename,
                    "page_number": page_num,
                    "chunk_index": chunk_idx,
                    "content": text,
                    "char_start": 0,
                    "char_end": len(text),
                })
                chunk_idx += 1
                continue

            # Sliding window with overlap
            start = 0
            while start < len(text):
                end = start + self.chunk_size

                # Try to break on paragraph or sentence boundary
                if end < len(text):
                    # Look backwards for paragraph break or period
                    window = text[start:end]
                    break_point = -1
                    for delimiter in ["\n\n", "\n", ". ", "? ", "! "]:
                        pos = window.rfind(delimiter)
                        if pos > self.chunk_size // 2:
                            break_point = pos + len(delimiter)
                            break
                    if break_point != -1:
                        end = start + break_point

                chunk_text_slice = text[start:end].strip()
                if chunk_text_slice:
                    chunk_id = f"{document_id}_c{chunk_idx}"
                    chunks.append({
                        "chunk_id": chunk_id,
                        "document_id": document_id,
                        "filename": filename,
                        "page_number": page_num,
                        "chunk_index": chunk_idx,
                        "content": chunk_text_slice,
                        "char_start": start,
                        "char_end": end,
                    })
                    chunk_idx += 1

                # Advance start window taking overlap into account
                start = end - self.chunk_overlap
                if start >= len(text) or end >= len(text):
                    break

        return chunks

    async def ingest_file(
        self,
        file_path: Path,
        filename: str,
        document_id: str = None
    ) -> Tuple[Dict[str, Any], int]:
        """
        Complete ingestion workflow:
        1. Extract text
        2. Chunk text
        3. Embed chunks
        4. Save to ChromaDB & update registry
        """
        doc_id = document_id or str(uuid.uuid4())
        file_size = os.path.getsize(file_path)
        ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else "txt"
        upload_date = datetime.now(timezone.utc).isoformat()

        # Check registry for duplicate file name
        existing_docs = vector_store.list_documents()
        for doc in existing_docs:
            if doc["filename"] == filename and doc["document_id"] != doc_id:
                # Remove prior vectors before re-ingesting duplicate name
                vector_store.delete_by_document_id(doc["document_id"])
                vector_store.remove_document_registry(doc["document_id"])

        # Register pending document
        doc_record = {
            "document_id": doc_id,
            "filename": filename,
            "file_type": ext,
            "file_size_bytes": file_size,
            "upload_date": upload_date,
            "status": "processing",
            "chunk_count": 0,
            "error_message": None,
            "file_path": str(file_path),
        }
        vector_store.register_document(doc_record)

        try:
            # 1. Extract text
            pages = self.extract_text_from_file(file_path, filename)
            
            # 2. Chunk text
            chunks = self.chunk_text(pages, doc_id, filename)
            if not chunks:
                raise ValueError("Document yielded 0 chunks.")

            # 3. Generate embeddings
            contents = [c["content"] for c in chunks]
            embeddings = await embedding_service.get_embeddings(contents)

            # 4. Remove any existing vectors for this doc_id
            vector_store.delete_by_document_id(doc_id)

            # 5. Save to ChromaDB
            vector_store.add_chunks(chunks, embeddings)

            # 6. Mark successful
            vector_store.update_document_status(
                document_id=doc_id,
                status="indexed",
                chunk_count=len(chunks),
                error_message=None
            )
            doc_record["status"] = "indexed"
            doc_record["chunk_count"] = len(chunks)

            return doc_record, len(chunks)

        except Exception as e:
            error_msg = str(e)
            vector_store.update_document_status(
                document_id=doc_id,
                status="failed",
                chunk_count=0,
                error_message=error_msg
            )
            doc_record["status"] = "failed"
            doc_record["error_message"] = error_msg
            raise


ingestion_service = IngestionService()
