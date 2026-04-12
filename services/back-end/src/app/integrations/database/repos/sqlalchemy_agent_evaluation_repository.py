from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import SQLAlchemyError

from app.domain_models.common.exceptions import StorageUnavailableError
from app.domain_models.common.ids import SessionId
from app.domain_models.evaluation.models import (
    BehaviorChange,
    ClosingSignal,
    EvaluationEvidence,
    SatisfactionClass,
    SessionEvaluation,
    TokenUsage,
)
from app.integrations.database.models.agent_evaluation_models import AgentSessionEvaluationModel
from app.integrations.database.sqlalchemy_database import SQLAlchemyDatabase


class SQLAlchemyAgentEvaluationRepository:
    def __init__(self, database: SQLAlchemyDatabase) -> None:
        self._database = database

    def upsert_evaluations(self, evaluations: tuple[SessionEvaluation, ...]) -> None:
        if not evaluations:
            return
        seen: set[str] = set()
        deduped: list[SessionEvaluation] = []
        for ev in evaluations:
            key = str(ev.session_id.value)
            if key not in seen:
                seen.add(key)
                deduped.append(ev)
        rows = [_to_row(ev) for ev in deduped]
        try:
            with self._database.session_scope() as session:
                stmt = insert(AgentSessionEvaluationModel).values(rows)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["session_id"],
                    set_={
                        col: stmt.excluded[col]
                        for col in rows[0]
                        if col != "session_id" and col != "created_at"
                    },
                )
                session.execute(stmt)
        except SQLAlchemyError as exc:
            raise StorageUnavailableError("Unable to upsert agent evaluations.") from exc

    def list_all(self) -> tuple[SessionEvaluation, ...]:
        try:
            with self._database.session_scope() as session:
                rows = (
                    session.execute(
                        select(AgentSessionEvaluationModel).order_by(
                            AgentSessionEvaluationModel.created_at.asc()
                        )
                    )
                    .scalars()
                    .all()
                )
                return tuple(_from_row(row) for row in rows)
        except SQLAlchemyError as exc:
            raise StorageUnavailableError("Unable to list agent evaluations.") from exc

    def find_by_session_id(self, session_id: SessionId) -> SessionEvaluation | None:
        try:
            with self._database.session_scope() as session:
                row = session.execute(
                    select(AgentSessionEvaluationModel).where(
                        AgentSessionEvaluationModel.session_id == session_id.value
                    )
                ).scalar_one_or_none()
                return _from_row(row) if row is not None else None
        except SQLAlchemyError as exc:
            raise StorageUnavailableError("Unable to find agent evaluation.") from exc


def _to_row(ev: SessionEvaluation) -> dict:
    return {
        "session_id": ev.session_id.value,
        "satisfaction": ev.satisfaction.value,
        "effort_score": ev.effort_score,
        "understanding_score": ev.understanding_score,
        "resolution_score": ev.resolution_score,
        "prompt_injection_detected": ev.prompt_injection_detected,
        "injection_snippets_json": json.dumps(list(ev.injection_snippets)),
        "objetivo_cliente": ev.objetivo_cliente,
        "mudanca_comportamental": ev.mudanca_comportamental.value if ev.mudanca_comportamental else None,
        "sinal_fechamento": ev.sinal_fechamento.value if ev.sinal_fechamento else None,
        "total_tokens": ev.token_usage.total_tokens if ev.token_usage else None,
    }


def _from_row(row: AgentSessionEvaluationModel) -> SessionEvaluation:
    snippets: list[str] = json.loads(row.injection_snippets_json)
    token_usage = TokenUsage(0, 0, row.total_tokens) if row.total_tokens is not None else None
    return SessionEvaluation(
        session_id=SessionId(value=row.session_id),
        satisfaction=SatisfactionClass(row.satisfaction),
        effort_score=row.effort_score,
        understanding_score=row.understanding_score,
        resolution_score=row.resolution_score,
        evidences=tuple(EvaluationEvidence(snippet=s) for s in snippets[:2]),
        objetivo_cliente=row.objetivo_cliente,
        mudanca_comportamental=BehaviorChange(row.mudanca_comportamental) if row.mudanca_comportamental else None,
        sinal_fechamento=ClosingSignal(row.sinal_fechamento) if row.sinal_fechamento else None,
        token_usage=token_usage,
        prompt_injection_detected=row.prompt_injection_detected,
        injection_snippets=tuple(snippets),
    )
