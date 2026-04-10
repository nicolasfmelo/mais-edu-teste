from __future__ import annotations

from app.domain_models.common.ids import DocumentId
from app.domain_models.indexing.models import DocumentChunk


class ChunkingEngine:
    """Pure chunking rules grouped in a stateless class."""

    def chunk_text(self, document_id: DocumentId, text: str, chunk_size: int = 280) -> tuple[DocumentChunk, ...]:
        normalized = " ".join(text.split())
        if not normalized:
            return tuple()

        chunks: list[DocumentChunk] = []
        for position, start in enumerate(range(0, len(normalized), chunk_size)):
            chunks.append(
                DocumentChunk(
                    document_id=document_id,
                    content=normalized[start : start + chunk_size],
                    position=position,
                )
            )
        return tuple(chunks)
