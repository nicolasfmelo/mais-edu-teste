from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from app.integrations.database.models.base import Base


class ConversationMetricsModel(Base):
    __tablename__ = "conversation_metrics"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(Uuid, nullable=False, index=True)
    messages_count: Mapped[int] = mapped_column(Integer, nullable=False)
    rag_hits: Mapped[int] = mapped_column(Integer, nullable=False)
    used_credit_check: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
