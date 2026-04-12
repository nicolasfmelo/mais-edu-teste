from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ConversationExportResult:
    object_key: str
    session_count: int
    exported_at: datetime
