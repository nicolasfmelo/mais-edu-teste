from __future__ import annotations

from app.domain_models.common.contracts import DocumentStore, KnowledgeRepository
from app.domain_models.common.ids import DocumentId
from app.domain_models.indexing.models import IndexingJob, UniversityRecord
from app.domain_models.rag.models import KnowledgeDocument
from app.engines.indexing.chunking_engine import ChunkingEngine


class IndexerService:
    def __init__(
        self,
        knowledge_repository: KnowledgeRepository,
        document_store: DocumentStore,
        chunking_engine: ChunkingEngine,
    ) -> None:
        self._knowledge_repository = knowledge_repository
        self._document_store = document_store
        self._chunking_engine = chunking_engine

    def import_universities(self, dataset_name: str, records: tuple[UniversityRecord, ...]) -> IndexingJob:
        document_ids: list[DocumentId] = []
        generated_chunks = 0

        for record in records:
            document_id = DocumentId.new()
            document_ids.append(document_id)

            document = KnowledgeDocument(
                id=document_id,
                title=f"{record.name} - {record.course}",
                content=record.as_text(),
                source=dataset_name,
            )
            chunks = self._chunking_engine.chunk_text(document_id=document_id, text=document.content)

            self._document_store.save_university_record(document_id=document_id, record=record)
            self._knowledge_repository.save_document(document)
            self._knowledge_repository.save_chunks(chunks)
            generated_chunks += len(chunks)

        return IndexingJob(
            dataset_name=dataset_name,
            imported_documents=len(records),
            generated_chunks=generated_chunks,
            document_ids=tuple(document_ids),
        )
