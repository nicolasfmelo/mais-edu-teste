from pathlib import Path

from app.domain_models.indexing.models import CatalogCourse, CatalogCourseDocument
from app.engines.indexing.course_markdown_parser import CourseMarkdownParser
from app.services.indexing.course_catalog_bootstrap_service import CourseCatalogBootstrapService


class FakeCourseCatalogRepository:
    def __init__(self) -> None:
        self.ensure_schema_called = False
        self.courses: tuple[CatalogCourse, ...] = tuple()

    def ensure_schema(self) -> None:
        self.ensure_schema_called = True

    def upsert_courses(self, courses: tuple[CatalogCourse, ...]) -> int:
        self.courses = courses
        return len(courses)


class FakeCourseCatalogDocumentSource:
    def __init__(self, documents: tuple[CatalogCourseDocument, ...]) -> None:
        self._documents = documents

    def list_documents(self) -> tuple[CatalogCourseDocument, ...]:
        return self._documents


def test_course_catalog_bootstrap_service_loads_courses_and_upserts(tmp_path: Path) -> None:
    dataset_dir = tmp_path / "datasets"
    dataset_dir.mkdir()
    (dataset_dir / "graduacao-administracao.md").write_text(
        """# Graduacao em Administracao

## Informacoes gerais
- Nivel: Graduacao
- Modalidade: EAD
- Tempo de formacao: 4 anos

## O que voce vai aprender
Aprende fundamentos de gestao.

## Onde aplicar no mercado de trabalho
Atua em operacoes administrativas.

## Grade curricular
- Fundamentos da Administracao
- Gestao Financeira
""",
        encoding="utf-8",
    )

    repository = FakeCourseCatalogRepository()
    document_source = FakeCourseCatalogDocumentSource(
        (
            CatalogCourseDocument(
                slug="graduacao-administracao",
                raw_text=(dataset_dir / "graduacao-administracao.md").read_text(encoding="utf-8"),
                source_path=Path("graduacao-administracao.md"),
            ),
        )
    )
    service = CourseCatalogBootstrapService(
        repository=repository,
        document_source=document_source,
        parser=CourseMarkdownParser(),
    )

    result = service.bootstrap()

    assert repository.ensure_schema_called is True
    assert result.loaded_courses == 1
    assert result.upserted_courses == 1
    assert repository.courses[0].slug == "graduacao-administracao"
