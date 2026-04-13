from __future__ import annotations

from app.domain_models.common.contracts import CourseCatalogDocumentSource, CourseCatalogRepository
from app.domain_models.indexing.models import CatalogBootstrapResult, CatalogCourse
from app.engines.indexing.course_markdown_parser import CourseMarkdownParser


class CourseCatalogBootstrapService:
    def __init__(
        self,
        repository: CourseCatalogRepository,
        document_source: CourseCatalogDocumentSource,
        parser: CourseMarkdownParser,
    ) -> None:
        self._repository = repository
        self._document_source = document_source
        self._parser = parser

    def bootstrap(self) -> CatalogBootstrapResult:
        self._repository.ensure_schema()
        courses = self._load_courses()
        upserted_courses = self._repository.upsert_courses(courses)
        return CatalogBootstrapResult(loaded_courses=len(courses), upserted_courses=upserted_courses)

    def _load_courses(self) -> tuple[CatalogCourse, ...]:
        documents = self._document_source.list_documents()
        return tuple(self._parser.parse_document(document) for document in documents)
