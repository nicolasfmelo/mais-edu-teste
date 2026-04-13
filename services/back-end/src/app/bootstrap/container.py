from __future__ import annotations

import logging

from fastapi import APIRouter

from app.bootstrap.settings import AppSettings
from app.delivery.http.conversation_export_handler import ConversationExportHandler
from app.delivery.http.conversation_analysis_handler import ConversationAnalysisHandler
from app.delivery.http.assistant_catalog_handler import AssistantCatalogHandler
from app.delivery.http.chat_handler import ChatHandler
from app.delivery.http.evaluation_handler import EvaluationHandler
from app.delivery.http.indexing_handler import IndexingHandler
from app.delivery.http.metrics_handler import MetricsHandler
from app.delivery.http.prompt_registry_handler import PromptRegistryHandler
from app.domain_models.agent.models import AssistantModel
from app.engines.agent.prompt_assembly_engine import PromptAssemblyEngine
from app.engines.evaluation.evaluations_summary_engine import EvaluationsSummaryEngine
from app.engines.evaluation.session_evaluation_engine import SessionEvaluationEngine
from app.engines.indexing.chunking_engine import ChunkingEngine
from app.engines.indexing.course_catalog_knowledge_engine import CourseCatalogKnowledgeEngine
from app.engines.indexing.course_markdown_parser import CourseMarkdownParser
from app.engines.metrics.metrics_summary_engine import MetricsSummaryEngine
from app.engines.prompt.prompt_engine import PromptEngine
from app.integrations.database.repos.sqlalchemy_agent_evaluation_repository import SQLAlchemyAgentEvaluationRepository
from app.integrations.database.repos.sqlalchemy_course_catalog_repository import SQLAlchemyCourseCatalogRepository
from app.integrations.database.repos.sqlalchemy_knowledge_repository import SQLAlchemyKnowledgeRepository
from app.integrations.database.repos.sqlalchemy_metrics_repository import SQLAlchemyMetricsRepository
from app.integrations.database.repos.sqlalchemy_metrics_job_repository import SQLAlchemyMetricsJobRepository
from app.integrations.database.repos.sqlalchemy_prompt_registry_repository import SQLAlchemyPromptRegistryRepository
from app.integrations.database.repos.sqlalchemy_session_repository import SQLAlchemySessionRepository
from app.integrations.database.sqlalchemy_database import SQLAlchemyDatabase
from app.integrations.external_apis.llm_proxy_gateway_client import LLMProxyGatewayClient
from app.integrations.llm_providers.fake_embedding_client import FakeEmbeddingClient
from app.integrations.local_files.markdown_institution_profile_source import MarkdownInstitutionProfileSource
from app.integrations.object_store.minio_conversation_export_store import MinioConversationExportStore
from app.integrations.object_store.minio_conversation_reader import MinioConversationReader
from app.integrations.object_store.minio_document_store import MinioDocumentStore
from app.services.agent.agent_service import AgentService
from app.services.agent.langgraph_course_agent import LangGraphCourseAgent
from app.services.chat.conversation_export_service import ConversationExportService
from app.services.evaluation.conversation_analysis_service import ConversationAnalysisService
from app.services.evaluation.langgraph_conversation_analysis_agent import LangGraphConversationAnalysisAgent
from app.services.chat.chat_service import ChatService
from app.services.indexing.course_catalog_knowledge_bootstrap_service import CourseCatalogKnowledgeBootstrapService
from app.services.evaluation.evaluation_service import EvaluationService
from app.services.indexing.course_catalog_bootstrap_service import CourseCatalogBootstrapService
from app.services.indexing.indexer_service import IndexerService
from app.services.agent.assistant_catalog_service import AssistantCatalogService
from app.services.metrics.metrics_service import MetricsService
from app.services.prompt.prompt_registry_service import PromptRegistryService
from app.services.rag.rag_service import RagService


logger = logging.getLogger(__name__)

_ASSISTANT_MODEL_METADATA: dict[str, tuple[str, str]] = {
    "us.anthropic.claude-sonnet-4-6": ("Claude Sonnet 4.6", "anthropic"),
    "us.anthropic.claude-haiku-4-5-20251001-v1:0": ("Claude Haiku 4.5", "anthropic"),
    "minimax.minimax-m2.5": ("Minimax M2.5", "minimax"),
    "us.amazon.nova-2-lite-v1:0": ("Amazon Nova 2 Lite", "amazon"),
}


def _build_assistant_models(settings: AppSettings) -> tuple[AssistantModel, ...]:
    models: list[AssistantModel] = []
    for index, key in enumerate(settings.assistant_model_allowlist):
        metadata = _ASSISTANT_MODEL_METADATA.get(key)
        label = metadata[0] if metadata else key
        provider = metadata[1] if metadata else key.split(".", 1)[0]
        models.append(
            AssistantModel(
                key=key,
                label=label,
                provider=provider,
                is_default=index == 0,
            )
        )
    return tuple(models)


class AppContainer:
    def __init__(self, settings: AppSettings | None = None) -> None:
        self._settings = settings or AppSettings.from_env()
        self._database = SQLAlchemyDatabase(self._settings.database_url)
        self._session_repository = SQLAlchemySessionRepository(self._database)
        self._metrics_repository = SQLAlchemyMetricsRepository(self._database)
        self._metrics_job_repository = SQLAlchemyMetricsJobRepository(database=self._database)
        self._agent_evaluation_repository = SQLAlchemyAgentEvaluationRepository(database=self._database)
        self._knowledge_repository = SQLAlchemyKnowledgeRepository(self._database)
        self._document_store = MinioDocumentStore()
        self._conversation_export_store = MinioConversationExportStore(
            endpoint=self._settings.minio_endpoint,
            access_key=self._settings.minio_access_key,
            secret_key=self._settings.minio_secret_key,
            bucket=self._settings.minio_export_bucket,
        )
        self._conversation_reader = MinioConversationReader(
            endpoint=self._settings.minio_endpoint,
            access_key=self._settings.minio_access_key,
            secret_key=self._settings.minio_secret_key,
            bucket=self._settings.minio_export_bucket,
        )
        self._embedding_client = FakeEmbeddingClient()
        self._ai_gateway_client = LLMProxyGatewayClient(base_url=self._settings.llm_proxy_base_url or "")
        self._assistant_models = _build_assistant_models(self._settings)
        self._institution_profile_source = MarkdownInstitutionProfileSource(
            profile_path=self._settings.institution_profile_path
        )
        self._institution_profile = self._institution_profile_source.load()

        self._prompt_assembly_engine = PromptAssemblyEngine(institution_profile=self._institution_profile)
        self._chunking_engine = ChunkingEngine()
        self._evaluation_engine = SessionEvaluationEngine()
        self._evaluations_summary_engine = EvaluationsSummaryEngine()
        self._metrics_summary_engine = MetricsSummaryEngine()
        self._prompt_engine = PromptEngine()
        self._course_catalog_knowledge_engine = CourseCatalogKnowledgeEngine()
        self._course_markdown_parser = CourseMarkdownParser()
        self._prompt_registry_repository = SQLAlchemyPromptRegistryRepository(
            database=self._database,
        )
        self._course_catalog_repository = SQLAlchemyCourseCatalogRepository(self._database)

        self._rag_service = RagService(
            knowledge_repository=self._knowledge_repository,
            embedding_client=self._embedding_client,
        )
        self._course_agent = LangGraphCourseAgent(
            rag_service=self._rag_service,
            ai_gateway_client=self._ai_gateway_client,
            prompt_assembly_engine=self._prompt_assembly_engine,
        )
        self._agent_service = AgentService(
            course_agent=self._course_agent,
        )
        self._assistant_catalog_service = AssistantCatalogService(
            credit_balance_client=self._ai_gateway_client,
            assistant_models=self._assistant_models,
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
            evaluations_summary_engine=self._evaluations_summary_engine,
            agent_evaluation_repository=self._agent_evaluation_repository,
        )
        self._prompt_registry_service = PromptRegistryService(
            prompt_registry_repository=self._prompt_registry_repository,
            prompt_engine=self._prompt_engine,
        )
        self._conversation_export_service = ConversationExportService(
            session_repository=self._session_repository,
            export_store=self._conversation_export_store,
            metrics_job_repository=self._metrics_job_repository,
        )
        self._conversation_analysis_agent = LangGraphConversationAnalysisAgent(
            conversation_reader=self._conversation_reader,
            ai_gateway_client=self._ai_gateway_client,
        )
        self._conversation_analysis_service = ConversationAnalysisService(
            analysis_agent=self._conversation_analysis_agent,
            evaluations_summary_engine=self._evaluations_summary_engine,
            metrics_job_repository=self._metrics_job_repository,
            agent_evaluation_repository=self._agent_evaluation_repository,
        )
        self._course_catalog_bootstrap_service = (
            CourseCatalogBootstrapService(
                repository=self._course_catalog_repository,
                parser=self._course_markdown_parser,
                dataset_dir=self._settings.datasets_dir,
            )
        )
        self._course_catalog_knowledge_bootstrap_service = (
            CourseCatalogKnowledgeBootstrapService(
                knowledge_repository=self._knowledge_repository,
                parser=self._course_markdown_parser,
                knowledge_engine=self._course_catalog_knowledge_engine,
                chunking_engine=self._chunking_engine,
                dataset_dir=self._settings.datasets_dir,
            )
        )

    def build_router(self) -> APIRouter:
        router = APIRouter()
        router.include_router(AssistantCatalogHandler(assistant_catalog_service=self._assistant_catalog_service).router)
        router.include_router(ChatHandler(chat_service=self._chat_service).router)
        router.include_router(IndexingHandler(indexer_service=self._indexer_service).router)
        router.include_router(MetricsHandler(metrics_service=self._metrics_service, metrics_job_repository=self._metrics_job_repository).router)
        router.include_router(EvaluationHandler(evaluation_service=self._evaluation_service).router)
        router.include_router(PromptRegistryHandler(prompt_registry_service=self._prompt_registry_service).router)
        router.include_router(ConversationExportHandler(conversation_export_service=self._conversation_export_service).router)
        router.include_router(ConversationAnalysisHandler(conversation_analysis_service=self._conversation_analysis_service).router)
        return router

    def startup(self) -> None:
        self._database.create_schema()
        if not self._settings.indexing_bootstrap_enabled:
            logger.info("Skipping course catalog bootstrap because startup indexing is disabled.")
            return
        result = self._course_catalog_bootstrap_service.bootstrap()
        knowledge_result = self._course_catalog_knowledge_bootstrap_service.bootstrap()
        logger.info(
            "Course catalog bootstrap completed with %s loaded and %s upserted courses.",
            result.loaded_courses,
            result.upserted_courses,
        )
        logger.info(
            "Course knowledge bootstrap completed with %s indexed documents and %s generated chunks.",
            knowledge_result.indexed_documents,
            knowledge_result.generated_chunks,
        )
