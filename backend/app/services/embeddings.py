import re
import math
import hashlib
from typing import List
import httpx
from app.core.config import settings


STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't", "cannot", "could",
    "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from", "further", "had", "has", "have",
    "having", "he", "her", "here", "hers", "herself", "him", "himself", "his", "how", "i", "if", "in", "into", "is",
    "isn't", "it", "it's", "its", "itself", "me", "more", "most", "my", "myself", "no", "nor", "not", "of", "off", "on",
    "once", "only", "or", "other", "our", "ours", "out", "over", "own", "same", "she", "should", "so", "some", "such",
    "than", "that", "the", "their", "theirs", "them", "then", "there", "these", "they", "this", "those", "through",
    "to", "too", "under", "until", "up", "very", "was", "we", "were", "what", "when", "where", "which", "while", "who",
    "whom", "why", "with", "would", "you", "your", "yours", "yourself", "yourselves"
}


class LocalDeterministicEmbedder:
    """
    High-fidelity, deterministic, zero-dependency embedding generator (384 dimensions).
    Uses hashed content tokens (unigrams + bigrams) with stopword removal, sublinear tf weighting,
    and L2-normalization for sharp semantic discrimination without heavy ML runtime weights.
    """
    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def _tokenize(self, text: str) -> List[tuple[str, float]]:
        text = text.lower()
        raw_words = re.findall(r"\b[a-z0-9_-]{2,}\b", text)
        filtered_words = [w for w in raw_words if w not in STOPWORDS]

        tokens: List[tuple[str, float]] = []
        # Content unigrams (weight 3.0)
        for w in filtered_words:
            tokens.append((f"w:{w}", 3.0))

        # Word bigrams for phrasal matching (weight 2.5)
        for i in range(len(filtered_words) - 1):
            tokens.append((f"bi:{filtered_words[i]}_{filtered_words[i+1]}", 2.5))

        # Include essential domain keywords even if short
        for w in raw_words:
            if len(w) >= 3 and w not in STOPWORDS:
                tokens.append((f"stem:{w[:4]}", 1.5))

        return tokens

    def embed_text(self, text: str) -> List[float]:
        token_tuples = self._tokenize(text)
        if not token_tuples:
            return [0.0] * self.dimension

        vec = [0.0] * self.dimension
        token_weights: dict[str, float] = {}
        for token, w in token_tuples:
            token_weights[token] = token_weights.get(token, 0.0) + w

        for token, total_w in token_weights.items():
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dimension
            sign = 1.0 if ((h >> 32) & 1) == 0 else -1.0
            tf = 1.0 + math.log(1.0 + total_w)
            vec[idx] += sign * tf

        # L2 normalize
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        return vec


class EmbeddingService:
    def __init__(self):
        self.local_embedder = LocalDeterministicEmbedder(dimension=384)

    async def get_embedding(self, text: str) -> List[float]:
        """Generate embedding vector for a single text."""
        embeddings = await self.get_embeddings([text])
        return embeddings[0]

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embedding vectors for a list of texts."""
        provider = settings.EMBEDDING_PROVIDER.lower()

        # 1. OpenAI provider
        if provider == "openai" and settings.OPENAI_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    resp = await client.post(
                        "https://api.openai.com/v1/embeddings",
                        headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                        json={
                            "input": texts,
                            "model": "text-embedding-3-small",
                        },
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    return [item["embedding"] for item in data["data"]]
            except Exception as e:
                print(f"[EmbeddingService] OpenAI embedding failed ({e}), falling back to local embedder.")

        # 2. Gemini provider
        elif provider == "gemini" and settings.GEMINI_API_KEY:
            try:
                results = []
                async with httpx.AsyncClient(timeout=30.0) as client:
                    for text in texts:
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:embedContent?key={settings.GEMINI_API_KEY}"
                        resp = await client.post(
                            url,
                            json={
                                "model": "models/text-embedding-004",
                                "content": {"parts": [{"text": text}]},
                            },
                        )
                        resp.raise_for_status()
                        data = resp.json()
                        results.append(data["embedding"]["values"])
                return results
            except Exception as e:
                print(f"[EmbeddingService] Gemini embedding failed ({e}), falling back to local embedder.")

        # 3. Ollama provider
        elif provider == "ollama":
            try:
                results = []
                async with httpx.AsyncClient(timeout=30.0) as client:
                    for text in texts:
                        resp = await client.post(
                            f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/embeddings",
                            json={
                                "model": "nomic-embed-text",
                                "prompt": text,
                            },
                        )
                        resp.raise_for_status()
                        data = resp.json()
                        results.append(data["embedding"])
                return results
            except Exception as e:
                print(f"[EmbeddingService] Ollama embedding failed ({e}), falling back to local embedder.")

        # Default local embedder (zero dependencies, fast, deterministic)
        return [self.local_embedder.embed_text(t) for t in texts]


embedding_service = EmbeddingService()
