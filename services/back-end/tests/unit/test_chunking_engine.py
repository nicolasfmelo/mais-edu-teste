from app.domain_models.common.ids import DocumentId
from app.engines.indexing.chunking_engine import ChunkingEngine


def test_chunking_engine_splits_text() -> None:
    engine = ChunkingEngine()
    chunks = engine.chunk_text(document_id=DocumentId.new(), text="a" * 600, chunk_size=200)

    assert len(chunks) == 3
    assert chunks[0].position == 0
    assert chunks[-1].position == 2
