from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.domain_models.common.exceptions import StorageUnavailableError
from app.domain_models.common.ids import SessionId
from app.domain_models.metrics.models import ConversationMetrics
from app.integrations.database.models.metrics_models import ConversationMetricsModel
from app.integrations.database.sqlalchemy_database import SQLAlchemyDatabase


class SQLAlchemyMetricsRepository:
    def __init__(self, database: SQLAlchemyDatabase) -> None:
        self._database = database

    def save(self, metrics: ConversationMetrics) -> None:
        try:
            with self._database.session_scope() as session:
                session.add(
                    ConversationMetricsModel(
                        session_id=metrics.session_id.value,
                        messages_count=metrics.messages_count,
                        rag_hits=metrics.rag_hits,
                        used_credit_check=metrics.used_credit_check,
                    )
                )
        except SQLAlchemyError as exc:
            raise StorageUnavailableError("Unable to save conversation metrics.") from exc

    def list_all(self) -> tuple[ConversationMetrics, ...]:
        try:
            with self._database.session_scope() as session:
                rows = session.execute(
                    select(ConversationMetricsModel).order_by(ConversationMetricsModel.created_at.asc())
                ).scalars().all()
                return tuple(
                    ConversationMetrics(
                        session_id=SessionId(value=row.session_id),
                        messages_count=row.messages_count,
                        rag_hits=row.rag_hits,
                        used_credit_check=row.used_credit_check,
                    )
                    for row in rows
                )
        except SQLAlchemyError as exc:
            raise StorageUnavailableError("Unable to list conversation metrics.") from exc
