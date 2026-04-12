from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from uuid import UUID, uuid5

from app.domain_models.common.ids import DocumentId


@dataclass(frozen=True)
class UniversityRecord:
    name: str
    course: str
    modality: str
    city: str
    summary: str

    def as_text(self) -> str:
        return (
            f"Universidade: {self.name}\n"
            f"Curso: {self.course}\n"
            f"Modalidade: {self.modality}\n"
            f"Cidade: {self.city}\n"
            f"Resumo: {self.summary}"
        )


@dataclass(frozen=True)
class DocumentChunk:
    document_id: DocumentId
    content: str
    position: int


@dataclass(frozen=True)
class IndexingJob:
    dataset_name: str
    imported_documents: int
    generated_chunks: int
    document_ids: tuple[DocumentId, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CatalogCourseSource:
    slug: str
    title: str
    level: str
    modality: str
    duration_text: str
    learning_summary: str
    market_application: str
    curriculum_items: tuple[str, ...]
    source_path: Path


@dataclass(frozen=True)
class CatalogCourse:
    id: UUID
    slug: str
    title: str
    level: str
    modality: str
    duration_text: str
    learning_summary: str
    market_application: str
    curriculum_items: tuple[str, ...]
    source_path: str

    @classmethod
    def from_source(cls, source: CatalogCourseSource) -> "CatalogCourse":
        return cls(
            id=uuid5(UUID("6ba7b811-9dad-11d1-80b4-00c04fd430c8"), f"mais-a-educ-course:{source.slug}"),
            slug=source.slug,
            title=source.title,
            level=source.level,
            modality=source.modality,
            duration_text=source.duration_text,
            learning_summary=source.learning_summary,
            market_application=source.market_application,
            curriculum_items=source.curriculum_items,
            source_path=source.source_path.as_posix(),
        )

    @property
    def curriculum_text(self) -> str:
        return "\n".join(self.curriculum_items)

    @property
    def search_text(self) -> str:
        return " ".join(
            (
                self.title,
                self.level,
                self.modality,
                self.duration_text,
                self.learning_summary,
                self.market_application,
                " ".join(self.curriculum_items),
            )
        )


@dataclass(frozen=True)
class CatalogBootstrapResult:
    loaded_courses: int
    upserted_courses: int


@dataclass(frozen=True)
class CatalogKnowledgeBootstrapResult:
    loaded_courses: int
    indexed_documents: int
    generated_chunks: int
