from __future__ import annotations

from fastapi import APIRouter

from app.delivery.schemas.indexing_schemas import IndexUniversitiesRequestSchema, IndexUniversitiesResponseSchema
from app.services.indexing.indexer_service import IndexerService


class IndexingHandler:
    def __init__(self, indexer_service: IndexerService) -> None:
        self._indexer_service = indexer_service
        self.router = APIRouter(prefix="/api/indexing", tags=["indexing"])
        self.router.add_api_route(
            "/universities/import",
            self.import_universities,
            methods=["POST"],
            response_model=IndexUniversitiesResponseSchema,
        )

    async def import_universities(self, body: IndexUniversitiesRequestSchema) -> IndexUniversitiesResponseSchema:
        job = self._indexer_service.import_universities(
            dataset_name=body.dataset_name,
            records=body.to_domain_records(),
        )
        return IndexUniversitiesResponseSchema.from_domain(job)
