from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from app.integrations.database.models.base import Base


class CourseCatalogEntryModel(Base):
    __tablename__ = "course_catalog_entries"
    __table_args__ = (
        CheckConstraint("level in ('graduacao', 'pos-graduacao', 'mba')", name="ck_course_catalog_level"),
        CheckConstraint("modality in ('ead', 'remoto')", name="ck_course_catalog_modality"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    slug: Mapped[str] = mapped_column(Text, nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    level: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    modality: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    duration_text: Mapped[str] = mapped_column(Text, nullable=False)
    learning_summary: Mapped[str] = mapped_column(Text, nullable=False)
    market_application: Mapped[str] = mapped_column(Text, nullable=False)
    curriculum_text: Mapped[str] = mapped_column(Text, nullable=False)
    search_text: Mapped[str] = mapped_column(Text, nullable=False)
    source_path: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )
