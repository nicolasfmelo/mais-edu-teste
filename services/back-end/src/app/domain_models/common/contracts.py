from __future__ import annotations

from typing import Protocol

from app.domain_models.evaluation.models import SessionEvaluation
from app.domain_models.metrics.job_models import MetricsJob, MetricsJobStatus, MetricsJobType
from app.domain_models.agent.models import (
    CreditBalance,
    CreditStatus,
    GatewayPromptReply,
    GatewayPromptRequest,
    InstitutionProfile,
)
from app.domain_models.chat.models import ChatSession
from app.domain_models.common.ids import DocumentId, SessionId
from app.domain_models.indexing.models import CatalogCourse, CatalogCourseDocument, DocumentChunk, UniversityRecord
from app.domain_models.metrics.models import ConversationMetrics
from app.domain_models.prompt.models import (
    PromptActivation,
    PromptKey,
    PromptRegistration,
    PromptRegistryEntry,
    PromptVersionRegistration,
)
from app.domain_models.rag.models import KnowledgeDocument, RetrievedChunk


class SessionRepository(Protocol):
    def get_or_create(self, session_id: SessionId) -> ChatSession: ...
    def save(self, session: ChatSession) -> ChatSession: ...
    def find_by_id(self, session_id: SessionId) -> ChatSession: ...
    def list_all(self) -> tuple[ChatSession, ...]: ...


class KnowledgeRepository(Protocol):
    def save_document(self, document: KnowledgeDocument) -> None: ...
    def save_chunks(self, chunks: tuple[DocumentChunk, ...]) -> None: ...
    def search(self, query_text: str, query_embedding: tuple[float, ...], limit: int) -> tuple[RetrievedChunk, ...]: ...


class DocumentStore(Protocol):
    def save_university_record(self, document_id: DocumentId, record: UniversityRecord) -> None: ...


class EmbeddingClient(Protocol):
    def embed_text(self, text: str) -> tuple[float, ...]: ...


class InstitutionProfileSource(Protocol):
    def load(self) -> InstitutionProfile: ...


class CourseCatalogRepository(Protocol):
    def ensure_schema(self) -> None: ...
    def upsert_courses(self, courses: tuple[CatalogCourse, ...]) -> int: ...
    def search_courses(
        self,
        query: str | None = None,
        *,
        level: str | None = None,
        modality: str | None = None,
        limit: int = 5,
    ) -> tuple[CatalogCourse, ...]: ...


class CourseCatalogDocumentSource(Protocol):
    def list_documents(self) -> tuple[CatalogCourseDocument, ...]: ...


class CreditSystemClient(Protocol):
    def verify_credit(self, session_id: SessionId) -> CreditStatus: ...


class CreditBalanceClient(Protocol):
    def get_credit_balance(self, api_key: str) -> CreditBalance: ...


class AIGatewayClient(Protocol):
    def generate_reply(self, request: GatewayPromptRequest) -> GatewayPromptReply: ...


class MetricsRepository(Protocol):
    def save(self, metrics: ConversationMetrics) -> None: ...
    def list_all(self) -> tuple[ConversationMetrics, ...]: ...


class PromptRegistryRepository(Protocol):
    def list_entries(self) -> tuple[PromptRegistryEntry, ...]: ...
    def find_by_key(self, key: PromptKey) -> PromptRegistryEntry: ...
    def create_prompt(self, registration: PromptRegistration) -> PromptRegistryEntry: ...
    def create_version(self, registration: PromptVersionRegistration) -> PromptRegistryEntry: ...
    def activate_version(self, entry: PromptRegistryEntry) -> PromptRegistryEntry: ...


class AgentEvaluationRepository(Protocol):
    def upsert_evaluations(self, evaluations: tuple[SessionEvaluation, ...]) -> None: ...
    def list_all(self) -> tuple[SessionEvaluation, ...]: ...
    def find_by_session_id(self, session_id: SessionId) -> SessionEvaluation | None: ...


class MetricsJobRepository(Protocol):
    def create_job(self, job_type: MetricsJobType) -> MetricsJob: ...
    def update_job(self, job_id: int, status: MetricsJobStatus, **kwargs: object) -> MetricsJob: ...
    def get_latest_job(self, job_type: MetricsJobType) -> MetricsJob | None: ...
