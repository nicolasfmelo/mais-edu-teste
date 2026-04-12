from __future__ import annotations

from app.domain_models.common.contracts import AgentEvaluationRepository, MetricsJobRepository
from app.domain_models.evaluation.models import ConversationAnalysisResult
from app.domain_models.metrics.job_models import MetricsJobStatus, MetricsJobType
from app.engines.evaluation.evaluations_summary_engine import EvaluationsSummaryEngine
from app.services.evaluation.langgraph_conversation_analysis_agent import LangGraphConversationAnalysisAgent


class ConversationAnalysisService:
    def __init__(
        self,
        analysis_agent: LangGraphConversationAnalysisAgent,
        evaluations_summary_engine: EvaluationsSummaryEngine,
        metrics_job_repository: MetricsJobRepository,
        agent_evaluation_repository: AgentEvaluationRepository,
    ) -> None:
        self._analysis_agent = analysis_agent
        self._evaluations_summary_engine = evaluations_summary_engine
        self._metrics_job_repository = metrics_job_repository
        self._agent_evaluation_repository = agent_evaluation_repository

    def analyze_all(self, api_key: str, model_id: str | None = None) -> ConversationAnalysisResult:
        job = self._metrics_job_repository.create_job(MetricsJobType.ANALYSIS)
        try:
            evaluations = self._analysis_agent.analyze(api_key=api_key, model_id=model_id)
            summary = self._evaluations_summary_engine.build_summary(evaluations)
            result = ConversationAnalysisResult(evaluations=evaluations, summary=summary)
            self._agent_evaluation_repository.upsert_evaluations(evaluations)
            self._metrics_job_repository.update_job(
                job.id,
                MetricsJobStatus.DONE,
                processed_count=len(result.evaluations),
            )
            return result
        except Exception as exc:
            self._metrics_job_repository.update_job(job.id, MetricsJobStatus.ERROR, error_message=str(exc))
            raise
