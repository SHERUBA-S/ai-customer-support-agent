import pytest
from app.services.rag_pipeline import rag_pipeline
from app.schemas.chat import ChatMessage


@pytest.mark.asyncio
async def test_rag_answers_with_sources():
    response = await rag_pipeline.run("What is the return window for products?")
    assert response.answer is not None
    assert response.insufficient_context is False
    assert len(response.sources) > 0
    # Source metadata checks
    first_source = response.sources[0]
    assert first_source.document_name == "refunds_and_returns_policy.md"
    assert first_source.relevant_excerpt != ""
    assert first_source.relevance_score > 0.0


@pytest.mark.asyncio
async def test_rag_insufficient_context():
    response = await rag_pipeline.run("What is the speed of light in deep space vacuum?")
    assert response.insufficient_context is True
    assert "couldn't find enough information" in response.answer.lower()
    assert len(response.sources) == 0


@pytest.mark.asyncio
async def test_rag_follow_up_context():
    # Turn 1
    t1_response = await rag_pipeline.run("What is the refund policy?")
    assert len(t1_response.sources) > 0

    # Turn 2: Follow-up question relying on previous turn
    history = [
        ChatMessage(role="user", content="What is the refund policy?"),
        ChatMessage(role="assistant", content=t1_response.answer),
    ]
    t2_response = await rag_pipeline.run("How many days do I have?", history=history)
    assert t2_response.insufficient_context is False
    assert len(t2_response.sources) > 0
    assert any("refund" in s.document_name.lower() for s in t2_response.sources)
