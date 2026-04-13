from pathlib import Path

from app.integrations.local_files.course_catalog_document_source import CourseCatalogDocumentSource


def test_course_catalog_document_source_reads_markdown_documents(tmp_path: Path) -> None:
    dataset_dir = tmp_path / "datasets"
    dataset_dir.mkdir()
    (dataset_dir / "mba-gestao-projetos.md").write_text("# Titulo\nconteudo", encoding="utf-8")

    documents = CourseCatalogDocumentSource(dataset_dir=dataset_dir).list_documents()

    assert len(documents) == 1
    assert documents[0].slug == "mba-gestao-projetos"
    assert documents[0].raw_text == "# Titulo\nconteudo"
    assert documents[0].source_path == Path("mba-gestao-projetos.md")
