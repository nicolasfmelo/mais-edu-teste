from __future__ import annotations

from app.domain_models.indexing.models import DocumentChunk
from app.domain_models.rag.models import KnowledgeDocument, RetrievedChunk


class QdrantKnowledgeRepository:
    def __init__(self) -> None:
        self._documents: dict[str, KnowledgeDocument] = {}
        self._chunks: list[DocumentChunk] = []

    def save_document(self, document: KnowledgeDocument) -> None:
        self._documents[str(document.id)] = document

    def save_chunks(self, chunks: tuple[DocumentChunk, ...]) -> None:
        self._chunks.extend(chunks)

    def search(self, query_embedding: tuple[float, ...], limit: int) -> tuple[RetrievedChunk, ...]:
        del query_embedding
        ranked_chunks = [
            RetrievedChunk(
                document_id=chunk.document_id,
                content=chunk.content,
                score=max(0.1, 1 - (chunk.position * 0.1)),
            )
            for chunk in self._chunks[:limit]
        ]
        return tuple(ranked_chunks)
