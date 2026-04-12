from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class MetricsJobType(str, Enum):
    EXPORT = "export"
    ANALYSIS = "analysis"


class MetricsJobStatus(str, Enum):
    RUNNING = "running"
    DONE = "done"
    ERROR = "error"


@dataclass(frozen=True)
class MetricsJob:
    id: int
    job_type: MetricsJobType
    status: MetricsJobStatus
    started_at: datetime
    finished_at: datetime | None = None
    session_count: int | None = None
    object_key: str | None = None
    processed_count: int | None = None
    error_message: str | None = None
