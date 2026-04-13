from __future__ import annotations

from pathlib import Path

from app.domain_models.indexing.models import CatalogCourseDocument


class CourseCatalogDocumentSource:
    def __init__(self, dataset_dir: Path) -> None:
        self._dataset_dir = dataset_dir

    def list_documents(self) -> tuple[CatalogCourseDocument, ...]:
        if not self._dataset_dir.exists():
            raise FileNotFoundError(f"Dataset directory not found: {self._dataset_dir}")

        files = sorted(self._dataset_dir.glob("*.md"))
        return tuple(
            CatalogCourseDocument(
                slug=file_path.stem,
                raw_text=file_path.read_text(encoding="utf-8").strip(),
                source_path=file_path.relative_to(self._dataset_dir),
            )
            for file_path in files
        )
