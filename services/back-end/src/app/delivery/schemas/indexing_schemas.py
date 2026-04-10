from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from app.domain_models.indexing.models import IndexingJob, UniversityRecord


class UniversityRecordSchema(BaseModel):
    name: str = Field(min_length=1)
    course: str = Field(min_length=1)
    modality: str = Field(min_length=1)
    city: str = Field(min_length=1)
    summary: str = Field(min_length=1)

    def to_domain(self) -> UniversityRecord:
        return UniversityRecord(
            name=self.name,
            course=self.course,
            modality=self.modality,
            city=self.city,
            summary=self.summary,
        )


class IndexUniversitiesRequestSchema(BaseModel):
    dataset_name: str = Field(min_length=1)
    records: list[UniversityRecordSchema]

    def to_domain_records(self) -> tuple[UniversityRecord, ...]:
        return tuple(record.to_domain() for record in self.records)


class IndexUniversitiesResponseSchema(BaseModel):
    dataset_name: str
    imported_documents: int
    generated_chunks: int
    document_ids: list[UUID]

    @classmethod
    def from_domain(cls, job: IndexingJob) -> "IndexUniversitiesResponseSchema":
        return cls(
            dataset_name=job.dataset_name,
            imported_documents=job.imported_documents,
            generated_chunks=job.generated_chunks,
            document_ids=[document_id.value for document_id in job.document_ids],
        )
