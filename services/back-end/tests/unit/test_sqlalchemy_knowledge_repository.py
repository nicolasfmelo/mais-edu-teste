from app.domain_models.common.ids import DocumentId
from app.domain_models.indexing.models import DocumentChunk
from app.domain_models.rag.models import KnowledgeDocument
from app.integrations.database.repos.sqlalchemy_knowledge_repository import SQLAlchemyKnowledgeRepository
from app.integrations.database.sqlalchemy_database import SQLAlchemyDatabase


def test_sqlalchemy_knowledge_repository_persists_and_searches_chunks(tmp_path) -> None:  # noqa: ANN001
    database = SQLAlchemyDatabase(f"sqlite+pysqlite:///{tmp_path / 'knowledge.db'}")
    database.create_schema()
    repository = SQLAlchemyKnowledgeRepository(database)
    document_id = DocumentId.new()

    repository.save_document(
        KnowledgeDocument(
            id=document_id,
            title="Pos-graduacao em Ciencia de Dados",
            content="Curso sobre analytics, python e machine learning.",
            source="dataset.md",
        )
    )
    repository.save_chunks(
        (
            DocumentChunk(
                document_id=document_id,
                content="Curso sobre analytics, python e machine learning.",
                position=0,
            ),
        )
    )

    chunks = repository.search(query_text="Quero estudar python para dados", query_embedding=(1.0, 0.5), limit=3)

    assert len(chunks) == 1
    assert chunks[0].document_id == document_id
    assert "python" in chunks[0].content.lower()
