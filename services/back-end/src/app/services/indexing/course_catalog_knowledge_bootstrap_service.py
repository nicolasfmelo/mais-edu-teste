from __future__ import annotations

from app.domain_models.common.contracts import CourseCatalogDocumentSource, KnowledgeRepository
from app.domain_models.indexing.models import CatalogCourse, CatalogKnowledgeBootstrapResult
from app.engines.indexing.chunking_engine import ChunkingEngine
from app.engines.indexing.course_catalog_knowledge_engine import CourseCatalogKnowledgeEngine
from app.engines.indexing.course_markdown_parser import CourseMarkdownParser


class CourseCatalogKnowledgeBootstrapService:
    def __init__(
        self,
        knowledge_repository: KnowledgeRepository,
        document_source: CourseCatalogDocumentSource,
        parser: CourseMarkdownParser,
        knowledge_engine: CourseCatalogKnowledgeEngine,
        chunking_engine: ChunkingEngine,
    ) -> None:
        self._knowledge_repository = knowledge_repository
        self._document_source = document_source
        self._parser = parser
        self._knowledge_engine = knowledge_engine
        self._chunking_engine = chunking_engine

    def bootstrap(self) -> CatalogKnowledgeBootstrapResult:
        courses = self._load_courses()
        generated_chunks = 0

        for course in courses:
            document = self._knowledge_engine.build_document(course)
            chunks = self._chunking_engine.chunk_text(document_id=document.id, text=document.content)
            self._knowledge_repository.save_document(document)
            self._knowledge_repository.save_chunks(chunks)
            generated_chunks += len(chunks)

        return CatalogKnowledgeBootstrapResult(
            loaded_courses=len(courses),
            indexed_documents=len(courses),
            generated_chunks=generated_chunks,
        )

    def _load_courses(self) -> tuple[CatalogCourse, ...]:
        documents = self._document_source.list_documents()
        return tuple(self._parser.parse_document(document) for document in documents)
