from pathlib import Path

from app.domain_models.indexing.models import CatalogCourseDocument
from app.engines.indexing.course_markdown_parser import CourseMarkdownParser


def test_course_markdown_parser_extracts_catalog_course(tmp_path: Path) -> None:
    dataset_dir = tmp_path / "datasets"
    dataset_dir.mkdir()
    course_file = dataset_dir / "mba-gestao-projetos.md"
    course_file.write_text(
        """# MBA em Gestao de Projetos

## Informacoes gerais
- Nivel: MBA
- Modalidade: EAD
- Tempo de formacao: 12 meses

## O que voce vai aprender
Aprende a estruturar escopo, cronograma e governanca.

## Onde aplicar no mercado de trabalho
Atua em PMO, implantacoes e lideranca de projetos.

## Grade curricular
- Fundamentos de Projetos
- Metodologias Ageis
- Gestao de Riscos
""",
        encoding="utf-8",
    )

    parser = CourseMarkdownParser()
    course = parser.parse_document(
        CatalogCourseDocument(
            slug=course_file.stem,
            raw_text=course_file.read_text(encoding="utf-8"),
            source_path=Path("mba-gestao-projetos.md"),
        )
    )

    assert course.slug == "mba-gestao-projetos"
    assert course.title == "MBA em Gestao de Projetos"
    assert course.level == "mba"
    assert course.modality == "ead"
    assert course.duration_text == "12 meses"
    assert course.curriculum_items == (
        "Fundamentos de Projetos",
        "Metodologias Ageis",
        "Gestao de Riscos",
    )
    assert course.source_path == "mba-gestao-projetos.md"
    assert "PMO" in course.market_application
    assert "Metodologias Ageis" in course.search_text
