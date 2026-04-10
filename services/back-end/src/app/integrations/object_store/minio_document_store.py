from __future__ import annotations

from app.domain_models.common.ids import DocumentId
from app.domain_models.indexing.models import UniversityRecord


class MinioDocumentStore:
    def __init__(self) -> None:
        self._records: dict[str, UniversityRecord] = {}

    def save_university_record(self, document_id: DocumentId, record: UniversityRecord) -> None:
        self._records[str(document_id)] = record
