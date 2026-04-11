from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Uuid

from app.integrations.database.models.base import Base


class PromptRegistryEntryModel(Base):
    __tablename__ = "prompt_registry_entries"

    key: Mapped[str] = mapped_column(Text, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    versions: Mapped[list["PromptVersionModel"]] = relationship(
        back_populates="entry",
        cascade="all, delete-orphan",
        order_by="PromptVersionModel.version_number",
    )


class PromptVersionModel(Base):
    __tablename__ = "prompt_versions"
    __table_args__ = (
        UniqueConstraint("prompt_key", "version_number", name="uq_prompt_versions_key_number"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    prompt_key: Mapped[str] = mapped_column(
        Text,
        ForeignKey("prompt_registry_entries.key", ondelete="CASCADE"),
        nullable=False,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    template: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    entry: Mapped[PromptRegistryEntryModel] = relationship(back_populates="versions")
