from __future__ import annotations

import re

from sqlalchemy import delete, or_, select
from sqlalchemy.exc import SQLAlchemyError

from app.domain_models.common.exceptions import StorageUnavailableError
from app.domain_models.common.ids import DocumentId
from app.domain_models.indexing.models import DocumentChunk
from app.domain_models.rag.models import KnowledgeDocument, RetrievedChunk
from app.integrations.database.models.knowledge_models import KnowledgeChunkModel, KnowledgeDocumentModel
from app.integrations.database.sqlalchemy_database import SQLAlchemyDatabase


class SQLAlchemyKnowledgeRepository:
    def __init__(self, database: SQLAlchemyDatabase) -> None:
        self._database = database

    def save_document(self, document: KnowledgeDocument) -> None:
        try:
            with self._database.session_scope() as session:
                model = session.get(KnowledgeDocumentModel, document.id.value)
                if model is None:
                    session.add(
                        KnowledgeDocumentModel(
                            id=document.id.value,
                            title=document.title,
                            content=document.content,
                            source=document.source,
                        )
                    )
                    return

                model.title = document.title
                model.content = document.content
                model.source = document.source
        except SQLAlchemyError as exc:
            raise StorageUnavailableError("Unable to save knowledge document.") from exc

    def save_chunks(self, chunks: tuple[DocumentChunk, ...]) -> None:
        if not chunks:
            return

        document_id = chunks[0].document_id.value
        try:
            with self._database.session_scope() as session:
                session.execute(delete(KnowledgeChunkModel).where(KnowledgeChunkModel.document_id == document_id))
                session.add_all(
                    KnowledgeChunkModel(
                        document_id=chunk.document_id.value,
                        position=chunk.position,
                        content=chunk.content,
                    )
                    for chunk in chunks
                )
        except SQLAlchemyError as exc:
            raise StorageUnavailableError("Unable to save knowledge chunks.") from exc

    def search(self, query_text: str, query_embedding: tuple[float, ...], limit: int) -> tuple[RetrievedChunk, ...]:
        del query_embedding

        query_terms = self._tokenize_query(query_text)
        try:
            with self._database.session_scope() as session:
                statement = select(KnowledgeChunkModel)
                if query_terms:
                    statement = statement.where(
                        or_(*(KnowledgeChunkModel.content.ilike(f"%{term}%") for term in query_terms))
                    )

                rows = session.execute(statement).scalars().all()
                ranked_rows = sorted(
                    rows,
                    key=lambda row: (-self._score_row(row.content, query_terms), row.position),
                )
                return tuple(
                    RetrievedChunk(
                        document_id=DocumentId(value=row.document_id),
                        content=row.content,
                        score=self._score_row(row.content, query_terms),
                    )
                    for row in ranked_rows[: max(1, limit)]
                )
        except SQLAlchemyError as exc:
            raise StorageUnavailableError("Unable to search knowledge chunks.") from exc

    def _tokenize_query(self, query: str) -> tuple[str, ...]:
        terms = [term for term in re.findall(r"[a-zA-Z0-9-]+", query.lower()) if len(term) >= 3]
        return tuple(dict.fromkeys(terms))

    def _score_row(self, content: str, query_terms: tuple[str, ...]) -> float:
        if not query_terms:
            return 0.1

        normalized_content = content.lower()
        matched_terms = sum(1 for term in query_terms if term in normalized_content)
        return max(0.1, matched_terms / len(query_terms))
