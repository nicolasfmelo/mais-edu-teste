from __future__ import annotations

from pathlib import Path

from app.domain_models.common.contracts import CourseCatalogRepository
from app.domain_models.indexing.models import CatalogBootstrapResult, CatalogCourse
from app.engines.indexing.course_markdown_parser import CourseMarkdownParser


class CourseCatalogBootstrapService:
    def __init__(
        self,
        repository: CourseCatalogRepository,
        parser: CourseMarkdownParser,
        dataset_dir: Path,
    ) -> None:
        self._repository = repository
        self._parser = parser
        self._dataset_dir = dataset_dir

    def bootstrap(self) -> CatalogBootstrapResult:
        self._repository.ensure_schema()
        courses = self._load_courses()
        upserted_courses = self._repository.upsert_courses(courses)
        return CatalogBootstrapResult(loaded_courses=len(courses), upserted_courses=upserted_courses)

    def _load_courses(self) -> tuple[CatalogCourse, ...]:
        if not self._dataset_dir.exists():
            raise FileNotFoundError(f"Dataset directory not found: {self._dataset_dir}")

        files = sorted(self._dataset_dir.glob("*.md"))
        return tuple(self._parser.parse_file(file_path=file_path, dataset_dir=self._dataset_dir) for file_path in files)
