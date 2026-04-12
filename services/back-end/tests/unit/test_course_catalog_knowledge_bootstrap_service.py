from pathlib import Path

from app.domain_models.common.ids import DocumentId
from app.domain_models.indexing.models import DocumentChunk
from app.domain_models.rag.models import KnowledgeDocument
from app.engines.indexing.chunking_engine import ChunkingEngine
from app.engines.indexing.course_catalog_knowledge_engine import CourseCatalogKnowledgeEngine
from app.engines.indexing.course_markdown_parser import CourseMarkdownParser
from app.services.indexing.course_catalog_knowledge_bootstrap_service import CourseCatalogKnowledgeBootstrapService


class FakeKnowledgeRepository:
    def __init__(self) -> None:
        self.documents: list[KnowledgeDocument] = []
        self.chunks: list[DocumentChunk] = []

    def save_document(self, document: KnowledgeDocument) -> None:
        self.documents.append(document)

    def save_chunks(self, chunks: tuple[DocumentChunk, ...]) -> None:
        self.chunks.extend(chunks)

    def search(self, query_text: str, query_embedding: tuple[float, ...], limit: int):  # noqa: ANN001
        return tuple()


def test_course_catalog_knowledge_bootstrap_service_indexes_dataset_into_knowledge_repository(
    tmp_path: Path,
) -> None:
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

    repository = FakeKnowledgeRepository()
    service = CourseCatalogKnowledgeBootstrapService(
        knowledge_repository=repository,
        parser=CourseMarkdownParser(),
        knowledge_engine=CourseCatalogKnowledgeEngine(),
        chunking_engine=ChunkingEngine(),
        dataset_dir=dataset_dir,
    )

    result = service.bootstrap()

    assert result.loaded_courses == 1
    assert result.indexed_documents == 1
    assert result.generated_chunks >= 1
    assert repository.documents[0].id == DocumentId(value=repository.documents[0].id.value)
