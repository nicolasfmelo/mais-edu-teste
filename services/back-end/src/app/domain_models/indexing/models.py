from __future__ import annotations

from dataclasses import dataclass, field

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
