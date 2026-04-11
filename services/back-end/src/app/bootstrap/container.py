from __future__ import annotations

import logging

from fastapi import APIRouter

from app.bootstrap.settings import AppSettings
from app.delivery.http.chat_handler import ChatHandler
from app.delivery.http.evaluation_handler import EvaluationHandler
from app.delivery.http.indexing_handler import IndexingHandler
from app.delivery.http.metrics_handler import MetricsHandler
from app.delivery.http.prompt_registry_handler import PromptRegistryHandler
from app.engines.evaluation.session_evaluation_engine import SessionEvaluationEngine
from app.engines.indexing.chunking_engine import ChunkingEngine
from app.engines.indexing.course_markdown_parser import CourseMarkdownParser
from app.engines.metrics.metrics_summary_engine import MetricsSummaryEngine
from app.engines.prompt.prompt_engine import PromptEngine
from app.integrations.database.repos.in_memory_metrics_repository import InMemoryMetricsRepository
from app.integrations.database.repos.in_memory_prompt_registry_repository import InMemoryPromptRegistryRepository
from app.integrations.database.repos.in_memory_session_repository import InMemorySessionRepository
from app.integrations.database.repos.postgres_course_catalog_repository import PostgresCourseCatalogRepository
from app.integrations.external_apis.fake_ai_gateway_client import FakeAIGatewayClient
from app.integrations.external_apis.fake_credit_system_client import FakeCreditSystemClient
from app.integrations.llm_providers.fake_embedding_client import FakeEmbeddingClient
from app.integrations.object_store.minio_document_store import MinioDocumentStore
from app.integrations.vector_store.qdrant_knowledge_repository import QdrantKnowledgeRepository
from app.services.agent.agent_service import AgentService
from app.services.chat.chat_service import ChatService
from app.services.evaluation.evaluation_service import EvaluationService
from app.services.indexing.course_catalog_bootstrap_service import CourseCatalogBootstrapService
from app.services.indexing.indexer_service import IndexerService
from app.services.metrics.metrics_service import MetricsService
from app.services.prompt.prompt_registry_service import PromptRegistryService
from app.services.rag.rag_service import RagService


logger = logging.getLogger(__name__)


class AppContainer:
    def __init__(self, settings: AppSettings | None = None) -> None:
        self._settings = settings or AppSettings.from_env()
        self._session_repository = InMemorySessionRepository()
        self._metrics_repository = InMemoryMetricsRepository()
        self._knowledge_repository = QdrantKnowledgeRepository()
        self._document_store = MinioDocumentStore()
        self._embedding_client = FakeEmbeddingClient()
        self._credit_system_client = FakeCreditSystemClient()
        self._ai_gateway_client = FakeAIGatewayClient()

        self._chunking_engine = ChunkingEngine()
        self._evaluation_engine = SessionEvaluationEngine()
        self._metrics_summary_engine = MetricsSummaryEngine()
        self._prompt_engine = PromptEngine()
        self._course_markdown_parser = CourseMarkdownParser()
        self._prompt_registry_repository = InMemoryPromptRegistryRepository(prompt_engine=self._prompt_engine)
        self._course_catalog_repository = (
            PostgresCourseCatalogRepository(self._settings.database_url) if self._settings.database_url else None
        )

        self._rag_service = RagService(
            knowledge_repository=self._knowledge_repository,
            embedding_client=self._embedding_client,
        )
        self._agent_service = AgentService(
            rag_service=self._rag_service,
            ai_gateway_client=self._ai_gateway_client,
            credit_system_client=self._credit_system_client,
        )
        self._metrics_service = MetricsService(
            metrics_repository=self._metrics_repository,
            summary_engine=self._metrics_summary_engine,
        )
        self._chat_service = ChatService(
            session_repository=self._session_repository,
            agent_service=self._agent_service,
            metrics_service=self._metrics_service,
        )
        self._indexer_service = IndexerService(
            knowledge_repository=self._knowledge_repository,
            document_store=self._document_store,
            chunking_engine=self._chunking_engine,
        )
        self._evaluation_service = EvaluationService(
            session_repository=self._session_repository,
            evaluation_engine=self._evaluation_engine,
        )
        self._prompt_registry_service = PromptRegistryService(
            prompt_registry_repository=self._prompt_registry_repository,
            prompt_engine=self._prompt_engine,
        )
        self._course_catalog_bootstrap_service = (
            CourseCatalogBootstrapService(
                repository=self._course_catalog_repository,
                parser=self._course_markdown_parser,
                dataset_dir=self._settings.datasets_dir,
            )
            if self._course_catalog_repository
            else None
        )

    def build_router(self) -> APIRouter:
        router = APIRouter()
        router.include_router(ChatHandler(chat_service=self._chat_service).router)
        router.include_router(IndexingHandler(indexer_service=self._indexer_service).router)
        router.include_router(MetricsHandler(metrics_service=self._metrics_service).router)
        router.include_router(EvaluationHandler(evaluation_service=self._evaluation_service).router)
        router.include_router(PromptRegistryHandler(prompt_registry_service=self._prompt_registry_service).router)
        return router

    def startup(self) -> None:
        if not self._settings.indexing_bootstrap_enabled:
            logger.info("Skipping course catalog bootstrap because startup indexing is disabled.")
            return
        if self._course_catalog_bootstrap_service is None:
            logger.info("Skipping course catalog bootstrap because DATABASE_URL is not configured.")
            return
        result = self._course_catalog_bootstrap_service.bootstrap()
        logger.info(
            "Course catalog bootstrap completed with %s loaded and %s upserted courses.",
            result.loaded_courses,
            result.upserted_courses,
        )
