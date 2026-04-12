from __future__ import annotations

from fastapi import APIRouter

from app.delivery.schemas.conversation_export_schemas import ConversationExportResponseSchema
from app.services.chat.conversation_export_service import ConversationExportService


class ConversationExportHandler:
    def __init__(self, conversation_export_service: ConversationExportService) -> None:
        self._service = conversation_export_service
        self.router = APIRouter(prefix="/api/conversations", tags=["conversations"])
        self.router.add_api_route(
            "/export",
            self.export_conversations,
            methods=["POST"],
            response_model=ConversationExportResponseSchema,
            status_code=202,
        )

    async def export_conversations(self) -> ConversationExportResponseSchema:
        result = self._service.export_all()
        return ConversationExportResponseSchema.from_domain(result)
