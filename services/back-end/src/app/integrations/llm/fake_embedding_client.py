from __future__ import annotations


class FakeEmbeddingClient:
    def embed_text(self, text: str) -> tuple[float, ...]:
        normalized = text.strip().lower()
        base = float(len(normalized) or 1)
        return (base, base / 2, base / 3)
