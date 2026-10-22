import pytest
from app.services.retrieval import retrieval_service


@pytest.mark.asyncio
async def test_retrieval_returns_relevant_chunks():
    results = await retrieval_service.retrieve("What is the refund policy?", top_k=3)
    assert len(results) > 0
    top_hit = results[0]
    assert "content" in top_hit
    assert "similarity" in top_hit
    assert top_hit["similarity"] > 0.08
    assert "refunds_and_returns_policy.md" in top_hit["metadata"]["filename"]


@pytest.mark.asyncio
async def test_retrieval_irrelevant_query():
    # Query completely outside the knowledge base
    results = await retrieval_service.retrieve("How do I build a nuclear reactor on Mars?", threshold=0.7)
    # High threshold should filter out irrelevant matches
    assert len(results) == 0
