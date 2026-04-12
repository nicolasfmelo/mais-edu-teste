from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from app.domain_models.chat.export_models import ConversationExportResult


class ConversationExportResponseSchema(BaseModel):
    object_key: str
    session_count: int
    exported_at: datetime

    @classmethod
    def from_domain(cls, result: ConversationExportResult) -> "ConversationExportResponseSchema":
        return cls(
            object_key=result.object_key,
            session_count=result.session_count,
            exported_at=result.exported_at,
        )
