from __future__ import annotations

from dataclasses import dataclass

from app.domain_models.common.ids import DocumentId, SessionId


@dataclass(frozen=True)
class KnowledgeDocument:
    id: DocumentId
    title: str
    content: str
    source: str


@dataclass(frozen=True)
class RetrievedChunk:
    document_id: DocumentId
    content: str
    score: float


@dataclass(frozen=True)
class RagQuery:
    session_id: SessionId
    question: str
    max_chunks: int = 3
