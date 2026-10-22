from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.vector_store import vector_store
from app.services.embeddings import embedding_service


class RetrievalService:
    def __init__(self):
        self.default_top_k = settings.TOP_K_RETRIEVAL
        self.default_threshold = settings.RELEVANCE_THRESHOLD

    async def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Embed the user query, search ChromaDB, and filter out low-similarity chunks.
        """
        k = top_k if top_k is not None else self.default_top_k
        min_score = threshold if threshold is not None else self.default_threshold

        query_clean = query.strip()
        if not query_clean:
            return []

        # 1. Generate query embedding
        query_vec = await embedding_service.get_embedding(query_clean)

        # 2. Query vector store
        raw_hits = vector_store.query(query_vec, top_k=k)

        # 3. Filter by relevance threshold
        filtered_hits: List[Dict[str, Any]] = []
        for hit in raw_hits:
            if hit["similarity"] >= min_score:
                filtered_hits.append(hit)

        return filtered_hits


retrieval_service = RetrievalService()
