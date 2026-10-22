import re
import uuid
from typing import List, Dict, Any, Optional
from app.schemas.chat import ChatResponse, SourceCitation, ChatMessage
from app.services.retrieval import retrieval_service
from app.services.llm_service import llm_service, INSUFFICIENT_CONTEXT_MESSAGE


class RAGPipeline:
    def __init__(self):
        pass

    def _normalize_query(self, query: str) -> str:
        """Strip extraneous whitespace and control characters."""
        clean = re.sub(r"[\r\n\t]+", " ", query).strip()
        # Remove repeated punctuation
        clean = re.sub(r"([?!.])\1+", r"\1", clean)
        return clean

    def _contextualize_followup(
        self,
        current_query: str,
        history: Optional[List[ChatMessage]]
    ) -> str:
        """
        Synthesize context for follow-up questions.
        Example:
        Previous: 'What is the refund policy?'
        Current: 'How many days do I have?'
        Contextualized Query: 'refund policy return window days limit'
        """
        if not history:
            return current_query

        # Look for ambiguous pronouns or short follow-ups
        followup_cues = ["it", "that", "this", "they", "those", "how many days", "how much", "how long", "what about", "and", "where"]
        lower_q = current_query.lower()
        is_followup = any(cue in lower_q for cue in followup_cues) or len(current_query.split()) <= 5

        if is_followup:
            # Find the most recent user question in history
            recent_user_questions = [
                m.content for m in history if m.role == "user"
            ]
            if recent_user_questions:
                last_q = recent_user_questions[-1]
                # Combine keywords from last query with current query for vector retrieval
                return f"{last_q} {current_query}"

        return current_query

    async def run(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        history: Optional[List[ChatMessage]] = None
    ) -> ChatResponse:
        """
        Execute end-to-end RAG retrieval, LLM synthesis, and source attribution.
        """
        conv_id = conversation_id or str(uuid.uuid4())
        normalized_q = self._normalize_query(message)

        if not normalized_q:
            return ChatResponse(
                answer="Please provide a valid question so I can assist you.",
                sources=[],
                conversation_id=conv_id,
                insufficient_context=True,
            )

        # 1. Expand query with conversation context for follow-up questions
        search_query = self._contextualize_followup(normalized_q, history)

        # 2. Retrieve relevant chunks with similarity threshold
        chunks = await retrieval_service.retrieve(search_query)

        # 3. Handle insufficient context
        if not chunks:
            return ChatResponse(
                answer=INSUFFICIENT_CONTEXT_MESSAGE,
                sources=[],
                conversation_id=conv_id,
                insufficient_context=True,
            )

        # 4. Generate answer via LLM
        history_dicts = [{"role": m.role, "content": m.content} for m in (history or [])]
        answer_text, insufficient = await llm_service.generate_answer(
            query=normalized_q,
            retrieved_chunks=chunks,
            conversation_history=history_dicts
        )

        # 5. Format verifiable source citations
        source_citations: List[SourceCitation] = []
        if not insufficient:
            for c in chunks:
                meta = c.get("metadata", {})
                content = c.get("content", "").strip()
                # Create a concise excerpt (first 250 chars or first two sentences)
                excerpt = content[:280] + ("..." if len(content) > 280 else "")

                citation = SourceCitation(
                    document_name=meta.get("filename", "Company Document"),
                    page_number=meta.get("page_number", 1),
                    relevant_excerpt=excerpt,
                    relevance_score=c.get("similarity", 0.0),
                    chunk_index=meta.get("chunk_index"),
                )
                source_citations.append(citation)

        return ChatResponse(
            answer=answer_text,
            sources=source_citations,
            conversation_id=conv_id,
            insufficient_context=insufficient,
            error=None,
        )


rag_pipeline = RAGPipeline()
