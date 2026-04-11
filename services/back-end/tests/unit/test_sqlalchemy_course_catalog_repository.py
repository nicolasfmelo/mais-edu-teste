from pathlib import Path

from app.domain_models.indexing.models import CatalogCourse
from app.integrations.database.repos.sqlalchemy_course_catalog_repository import SQLAlchemyCourseCatalogRepository
from app.integrations.database.sqlalchemy_database import SQLAlchemyDatabase


def test_sqlalchemy_course_catalog_repository_upserts_and_filters_courses(tmp_path: Path) -> None:
    database = SQLAlchemyDatabase(f"sqlite+pysqlite:///{tmp_path / 'catalog.db'}")
    repository = SQLAlchemyCourseCatalogRepository(database)
    repository.ensure_schema()

    course = CatalogCourse.from_source(
        slug="mba-gestao-projetos",
        title="MBA em Gestao de Projetos",
        level="mba",
        modality="ead",
        duration_text="12 meses",
        learning_summary="Aprende a planejar projetos.",
        market_application="Atua em PMO e implantacao.",
        curriculum_items=("Fundamentos de Projetos", "Metodologias Ageis"),
        source_path=Path("mba-gestao-projetos.md"),
    )

    upserted = repository.upsert_courses((course,))
    results = repository.search_courses(query="PMO", level="mba", modality="ead", limit=5)

    assert upserted == 1
    assert len(results) == 1
    assert results[0].slug == "mba-gestao-projetos"
