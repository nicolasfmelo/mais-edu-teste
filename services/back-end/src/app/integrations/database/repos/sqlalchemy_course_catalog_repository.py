from __future__ import annotations

import re

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import or_

from app.domain_models.common.exceptions import StorageUnavailableError
from app.domain_models.indexing.models import CatalogCourse
from app.integrations.database.models.course_catalog_models import CourseCatalogEntryModel
from app.integrations.database.sqlalchemy_database import SQLAlchemyDatabase


class SQLAlchemyCourseCatalogRepository:
    def __init__(self, database: SQLAlchemyDatabase) -> None:
        self._database = database

    def ensure_schema(self) -> None:
        self._database.create_schema()

    def upsert_courses(self, courses: tuple[CatalogCourse, ...]) -> int:
        if not courses:
            return 0

        try:
            with self._database.session_scope() as session:
                for course in courses:
                    row = session.execute(
                        select(CourseCatalogEntryModel).where(CourseCatalogEntryModel.slug == course.slug)
                    ).scalar_one_or_none()
                    if row is None:
                        session.add(self._to_model(course))
                        continue

                    row.title = course.title
                    row.level = course.level
                    row.modality = course.modality
                    row.duration_text = course.duration_text
                    row.learning_summary = course.learning_summary
                    row.market_application = course.market_application
                    row.curriculum_text = course.curriculum_text
                    row.search_text = course.search_text
                    row.source_path = course.source_path
            return len(courses)
        except SQLAlchemyError as exc:
            raise StorageUnavailableError("Unable to upsert course catalog entries.") from exc

    def search_courses(
        self,
        query: str | None = None,
        *,
        level: str | None = None,
        modality: str | None = None,
        limit: int = 5,
    ) -> tuple[CatalogCourse, ...]:
        try:
            with self._database.session_scope() as session:
                statement = select(CourseCatalogEntryModel)
                if level is not None:
                    statement = statement.where(CourseCatalogEntryModel.level == level)
                if modality is not None:
                    statement = statement.where(CourseCatalogEntryModel.modality == modality)
                if query:
                    query_terms = self._tokenize_query(query)
                    if query_terms:
                        statement = statement.where(
                            or_(*(CourseCatalogEntryModel.search_text.ilike(f"%{term}%") for term in query_terms))
                        )
                    else:
                        statement = statement.where(CourseCatalogEntryModel.search_text.ilike(f"%{query}%"))

                rows = session.execute(
                    statement.order_by(CourseCatalogEntryModel.title.asc()).limit(max(1, limit))
                ).scalars().all()
                return tuple(self._to_domain(row) for row in rows)
        except SQLAlchemyError as exc:
            raise StorageUnavailableError("Unable to search course catalog entries.") from exc

    def _tokenize_query(self, query: str) -> tuple[str, ...]:
        terms = [term for term in re.findall(r"[a-zA-Z0-9-]+", query.lower()) if len(term) >= 3]
        return tuple(dict.fromkeys(terms))

    def _to_model(self, course: CatalogCourse) -> CourseCatalogEntryModel:
        return CourseCatalogEntryModel(
            id=course.id,
            slug=course.slug,
            title=course.title,
            level=course.level,
            modality=course.modality,
            duration_text=course.duration_text,
            learning_summary=course.learning_summary,
            market_application=course.market_application,
            curriculum_text=course.curriculum_text,
            search_text=course.search_text,
            source_path=course.source_path,
        )

    def _to_domain(self, row: CourseCatalogEntryModel) -> CatalogCourse:
        return CatalogCourse(
            id=row.id,
            slug=row.slug,
            title=row.title,
            level=row.level,
            modality=row.modality,
            duration_text=row.duration_text,
            learning_summary=row.learning_summary,
            market_application=row.market_application,
            curriculum_items=tuple(row.curriculum_text.splitlines()),
            source_path=row.source_path,
        )
