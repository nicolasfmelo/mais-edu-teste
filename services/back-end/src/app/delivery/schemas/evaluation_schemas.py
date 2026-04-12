from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel

from app.domain_models.evaluation.models import ConversationAnalysisResult, EvaluationsSummary, SessionEvaluation


class SessionEvaluationResponseSchema(BaseModel):
    session_id: UUID
    satisfaction: str
    effort_score: int
    understanding_score: int
    resolution_score: int
    evidences: list[str]
    objetivo_cliente: str = ""
    mudanca_comportamental: str | None = None
    sinal_fechamento: str | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None
    prompt_injection_detected: bool = False
    injection_snippets: list[str] = []

    @classmethod
    def from_domain(cls, evaluation: SessionEvaluation) -> "SessionEvaluationResponseSchema":
        return cls(
            session_id=evaluation.session_id.value,
            satisfaction=evaluation.satisfaction.value,
            effort_score=evaluation.effort_score,
            understanding_score=evaluation.understanding_score,
            resolution_score=evaluation.resolution_score,
            evidences=[evidence.snippet for evidence in evaluation.evidences],
            objetivo_cliente=evaluation.objetivo_cliente,
            mudanca_comportamental=evaluation.mudanca_comportamental.value if evaluation.mudanca_comportamental else None,
            sinal_fechamento=evaluation.sinal_fechamento.value if evaluation.sinal_fechamento else None,
            prompt_tokens=evaluation.token_usage.prompt_tokens if evaluation.token_usage else None,
            completion_tokens=evaluation.token_usage.completion_tokens if evaluation.token_usage else None,
            total_tokens=evaluation.token_usage.total_tokens if evaluation.token_usage else None,
            prompt_injection_detected=evaluation.prompt_injection_detected,
            injection_snippets=list(evaluation.injection_snippets),
        )


class EvaluationsSummaryResponseSchema(BaseModel):
    total_evaluated: int
    count_bom: int
    count_neutro: int
    count_ruim: int
    pct_bom: float
    pct_neutro: float
    pct_ruim: float
    indice_ia_operadora: float
    avg_effort: float
    avg_understanding: float
    avg_resolution: float
    total_tokens_used: int = 0
    count_mudanca_positiva: int = 0
    count_mudanca_neutra: int = 0
    count_mudanca_negativa: int = 0
    count_injection_detected: int = 0
    pct_injection_detected: float = 0.0

    @classmethod
    def from_domain(cls, summary: EvaluationsSummary) -> "EvaluationsSummaryResponseSchema":
        return cls(
            total_evaluated=summary.total_evaluated,
            count_bom=summary.count_bom,
            count_neutro=summary.count_neutro,
            count_ruim=summary.count_ruim,
            pct_bom=summary.pct_bom,
            pct_neutro=summary.pct_neutro,
            pct_ruim=summary.pct_ruim,
            indice_ia_operadora=summary.indice_ia_operadora,
            avg_effort=summary.avg_effort,
            avg_understanding=summary.avg_understanding,
            avg_resolution=summary.avg_resolution,
            total_tokens_used=summary.total_tokens_used,
            count_mudanca_positiva=summary.count_mudanca_positiva,
            count_mudanca_neutra=summary.count_mudanca_neutra,
            count_mudanca_negativa=summary.count_mudanca_negativa,
            count_injection_detected=summary.count_injection_detected,
            pct_injection_detected=summary.pct_injection_detected,
        )


class ConversationAnalysisRequestSchema(BaseModel):
    api_key: str
    model_id: str | None = None


class ConversationAnalysisResponseSchema(BaseModel):
    evaluations: list[SessionEvaluationResponseSchema]
    summary: EvaluationsSummaryResponseSchema

    @classmethod
    def from_domain(cls, result: ConversationAnalysisResult) -> "ConversationAnalysisResponseSchema":
        return cls(
            evaluations=[SessionEvaluationResponseSchema.from_domain(e) for e in result.evaluations],
            summary=EvaluationsSummaryResponseSchema.from_domain(result.summary),
        )


class AgentSessionListItemSchema(BaseModel):
    session_id: UUID
    satisfaction: str
    objetivo_cliente: str
    total_tokens: int | None
    prompt_injection_detected: bool
    effort_score: int
    understanding_score: int
    resolution_score: int
    mudanca_comportamental: str | None
    sinal_fechamento: str | None

    @classmethod
    def from_domain(cls, evaluation: SessionEvaluation) -> "AgentSessionListItemSchema":
        return cls(
            session_id=evaluation.session_id.value,
            satisfaction=evaluation.satisfaction.value,
            objetivo_cliente=evaluation.objetivo_cliente,
            total_tokens=evaluation.token_usage.total_tokens if evaluation.token_usage else None,
            prompt_injection_detected=evaluation.prompt_injection_detected,
            effort_score=evaluation.effort_score,
            understanding_score=evaluation.understanding_score,
            resolution_score=evaluation.resolution_score,
            mudanca_comportamental=evaluation.mudanca_comportamental.value if evaluation.mudanca_comportamental else None,
            sinal_fechamento=evaluation.sinal_fechamento.value if evaluation.sinal_fechamento else None,
        )


class AgentSessionMessageSchema(BaseModel):
    role: str
    content: str


class AgentSessionDetailSchema(BaseModel):
    session_id: UUID
    satisfaction: str
    objetivo_cliente: str
    effort_score: int
    understanding_score: int
    resolution_score: int
    mudanca_comportamental: str | None
    sinal_fechamento: str | None
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    prompt_injection_detected: bool
    injection_snippets: list[str]
    evidences: list[str]
    messages: list[AgentSessionMessageSchema]
    prompt_used: str

    @classmethod
    def from_domain(
        cls,
        evaluation: SessionEvaluation,
        messages: list[AgentSessionMessageSchema],
        prompt_used: str,
    ) -> "AgentSessionDetailSchema":
        return cls(
            session_id=evaluation.session_id.value,
            satisfaction=evaluation.satisfaction.value,
            objetivo_cliente=evaluation.objetivo_cliente,
            effort_score=evaluation.effort_score,
            understanding_score=evaluation.understanding_score,
            resolution_score=evaluation.resolution_score,
            mudanca_comportamental=evaluation.mudanca_comportamental.value if evaluation.mudanca_comportamental else None,
            sinal_fechamento=evaluation.sinal_fechamento.value if evaluation.sinal_fechamento else None,
            prompt_tokens=evaluation.token_usage.prompt_tokens if evaluation.token_usage else None,
            completion_tokens=evaluation.token_usage.completion_tokens if evaluation.token_usage else None,
            total_tokens=evaluation.token_usage.total_tokens if evaluation.token_usage else None,
            prompt_injection_detected=evaluation.prompt_injection_detected,
            injection_snippets=list(evaluation.injection_snippets),
            evidences=[e.snippet for e in evaluation.evidences],
            messages=messages,
            prompt_used=prompt_used,
        )
