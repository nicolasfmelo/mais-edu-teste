from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.domain_models.common.exceptions import StorageUnavailableError
from app.domain_models.metrics.job_models import MetricsJob, MetricsJobStatus, MetricsJobType
from app.integrations.database.models.metrics_job_models import MetricsJobModel
from app.integrations.database.sqlalchemy_database import SQLAlchemyDatabase


class SQLAlchemyMetricsJobRepository:
    def __init__(self, database: SQLAlchemyDatabase) -> None:
        self._database = database

    def create_job(self, job_type: MetricsJobType) -> MetricsJob:
        try:
            with self._database.session_scope() as session:
                row = MetricsJobModel(
                    job_type=job_type.value,
                    status=MetricsJobStatus.RUNNING.value,
                    started_at=datetime.now(timezone.utc),
                )
                session.add(row)
                session.flush()
                return self._to_domain(row)
        except SQLAlchemyError as exc:
            raise StorageUnavailableError("Unable to create metrics job.") from exc

    def update_job(self, job_id: int, status: MetricsJobStatus, **kwargs: object) -> MetricsJob:
        try:
            with self._database.session_scope() as session:
                row = session.get(MetricsJobModel, job_id)
                if row is None:
                    raise StorageUnavailableError(f"Metrics job {job_id} not found.")
                row.status = status.value
                row.finished_at = datetime.now(timezone.utc)
                for key, value in kwargs.items():
                    if hasattr(row, key):
                        setattr(row, key, value)
                return self._to_domain(row)
        except SQLAlchemyError as exc:
            raise StorageUnavailableError("Unable to update metrics job.") from exc

    def get_latest_job(self, job_type: MetricsJobType) -> MetricsJob | None:
        try:
            with self._database.session_scope() as session:
                row = session.execute(
                    select(MetricsJobModel)
                    .where(MetricsJobModel.job_type == job_type.value)
                    .order_by(MetricsJobModel.started_at.desc())
                    .limit(1)
                ).scalars().first()
                return self._to_domain(row) if row else None
        except SQLAlchemyError as exc:
            raise StorageUnavailableError("Unable to fetch latest metrics job.") from exc

    @staticmethod
    def _to_domain(row: MetricsJobModel) -> MetricsJob:
        return MetricsJob(
            id=row.id,
            job_type=MetricsJobType(row.job_type),
            status=MetricsJobStatus(row.status),
            started_at=row.started_at,
            finished_at=row.finished_at,
            session_count=row.session_count,
            object_key=row.object_key,
            processed_count=row.processed_count,
            error_message=row.error_message,
        )
