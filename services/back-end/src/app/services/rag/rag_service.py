from __future__ import annotations

from app.domain_models.common.contracts import EmbeddingClient, KnowledgeRepository
from app.domain_models.rag.models import RagQuery, RetrievedChunk


class RagService:
    def __init__(
        self,
        knowledge_repository: KnowledgeRepository,
        embedding_client: EmbeddingClient,
    ) -> None:
        self._knowledge_repository = knowledge_repository
        self._embedding_client = embedding_client

    def retrieve(self, query: RagQuery) -> tuple[RetrievedChunk, ...]:
        query_embedding = self._embedding_client.embed_text(query.question)
        return self._knowledge_repository.search(
            query_text=query.question,
            query_embedding=query_embedding,
            limit=query.max_chunks,
        )
