from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from app.integrations.database.models.base import Base


class AgentSessionEvaluationModel(Base):
    __tablename__ = "agent_session_evaluations"

    session_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    satisfaction: Mapped[str] = mapped_column(String(20), nullable=False)
    effort_score: Mapped[int] = mapped_column(Integer, nullable=False)
    understanding_score: Mapped[int] = mapped_column(Integer, nullable=False)
    resolution_score: Mapped[int] = mapped_column(Integer, nullable=False)
    prompt_injection_detected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    injection_snippets_json: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    objetivo_cliente: Mapped[str] = mapped_column(Text, nullable=False, default="")
    mudanca_comportamental: Mapped[str | None] = mapped_column(String(20), nullable=True)
    sinal_fechamento: Mapped[str | None] = mapped_column(String(20), nullable=True)
    total_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
