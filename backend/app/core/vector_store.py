import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from app.core.config import settings


class VectorStore:
    def __init__(self):
        self.persist_dir = settings.CHROMA_PERSIST_DIRECTORY
        os.makedirs(self.persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection_name = "customer_support_kb"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self.meta_file = Path(self.persist_dir) / "documents_registry.json"
        self._ensure_registry()

    def _ensure_registry(self):
        if not self.meta_file.exists():
            self._save_registry({})

    def _load_registry(self) -> Dict[str, Any]:
        try:
            if self.meta_file.exists():
                with open(self.meta_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"[VectorStore] Registry load error: {e}")
        return {}

    def _save_registry(self, registry: Dict[str, Any]):
        try:
            with open(self.meta_file, "w", encoding="utf-8") as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[VectorStore] Registry save error: {e}")

    def register_document(self, doc_data: Dict[str, Any]):
        registry = self._load_registry()
        registry[doc_data["document_id"]] = doc_data
        self._save_registry(registry)

    def get_document(self, document_id: str) -> Optional[Dict[str, Any]]:
        registry = self._load_registry()
        return registry.get(document_id)

    def list_documents(self) -> List[Dict[str, Any]]:
        registry = self._load_registry()
        return list(registry.values())

    def update_document_status(
        self,
        document_id: str,
        status: str,
        chunk_count: Optional[int] = None,
        error_message: Optional[str] = None
    ):
        registry = self._load_registry()
        if document_id in registry:
            registry[document_id]["status"] = status
            if chunk_count is not None:
                registry[document_id]["chunk_count"] = chunk_count
            if error_message is not None:
                registry[document_id]["error_message"] = error_message
            self._save_registry(registry)

    def remove_document_registry(self, document_id: str):
        registry = self._load_registry()
        if document_id in registry:
            del registry[document_id]
            self._save_registry(registry)

    def add_chunks(
        self,
        chunks: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ):
        """Add text chunks and embeddings to ChromaDB."""
        if not chunks:
            return

        ids = [c["chunk_id"] for c in chunks]
        documents = [c["content"] for c in chunks]
        metadatas = []
        for c in chunks:
            # Flatten metadata for ChromaDB compatibility
            meta = {
                "document_id": str(c.get("document_id", "")),
                "filename": str(c.get("filename", "")),
                "page_number": int(c.get("page_number", 1)),
                "chunk_index": int(c.get("chunk_index", 0)),
                "char_start": int(c.get("char_start", 0)),
                "char_end": int(c.get("char_end", 0)),
            }
            metadatas.append(meta)

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def query(
        self,
        query_embedding: List[float],
        top_k: int = 4
    ) -> List[Dict[str, Any]]:
        """Query vector database and return chunks with cosine similarity score."""
        count = self.collection.count()
        if count == 0:
            return []

        actual_k = min(top_k, count)
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=actual_k,
            include=["documents", "metadatas", "distances"]
        )

        hits: List[Dict[str, Any]] = []
        if not results or not results["documents"] or not results["documents"][0]:
            return hits

        docs = results["documents"][0]
        metas = results["metadatas"][0] if results["metadatas"] else [{}] * len(docs)
        distances = results["distances"][0] if results["distances"] else [1.0] * len(docs)

        for doc, meta, dist in zip(docs, metas, distances):
            # Chroma returns cosine distance in [0, 2] for cosine metric
            # Similarity = 1.0 - (distance / 2.0) or max(0, 1.0 - distance)
            similarity = max(0.0, min(1.0, 1.0 - (dist if dist <= 1.0 else (dist / 2.0))))
            hits.append({
                "content": doc,
                "metadata": meta,
                "distance": dist,
                "similarity": round(similarity, 4),
            })

        # Sort highest similarity first
        hits.sort(key=lambda x: x["similarity"], reverse=True)
        return hits

    def delete_by_document_id(self, document_id: str):
        """Remove all vector chunks for a specific document ID."""
        try:
            self.collection.delete(where={"document_id": document_id})
        except Exception as e:
            print(f"[VectorStore] Error deleting vectors for doc {document_id}: {e}")

    def count_total_chunks(self) -> int:
        return self.collection.count()

    def reset_collection(self):
        """Reset the vector collection."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        self._save_registry({})


vector_store = VectorStore()
