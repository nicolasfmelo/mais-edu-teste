from app.domain_models.common.ids import DocumentId, SessionId
from app.domain_models.rag.models import RagQuery
from app.domain_models.rag.models import RetrievedChunk
from app.services.rag.rag_service import RagService


class StubKnowledgeRepository:
    def __init__(self) -> None:
        self.query_text: str | None = None
        self.query_embedding: tuple[float, ...] | None = None

    def search(self, query_text: str, query_embedding: tuple[float, ...], limit: int):  # noqa: ANN001
        self.query_text = query_text
        self.query_embedding = query_embedding
        return (
            RetrievedChunk(
                document_id=DocumentId.new(),
                content="Curso: Pos-graduacao em Ciencia de Dados",
                score=0.9,
            ),
        )


class StubEmbeddingClient:
    def embed_text(self, text: str) -> tuple[float, ...]:
        return (float(len(text)),)


def test_rag_service_retrieves_chunks_from_knowledge_repository() -> None:
    repository = StubKnowledgeRepository()
    service = RagService(
        knowledge_repository=repository,
        embedding_client=StubEmbeddingClient(),
    )

    chunks = service.retrieve(RagQuery(session_id=SessionId.new(), question="Quero estudar dados", max_chunks=3))

    assert len(chunks) == 1
    assert "Ciencia de Dados" in chunks[0].content
    assert repository.query_text == "Quero estudar dados"
    assert repository.query_embedding == (19.0,)
