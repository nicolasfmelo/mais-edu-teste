from __future__ import annotations

from collections.abc import Sequence

import psycopg

from app.domain_models.indexing.models import CatalogCourse


class PostgresCourseCatalogRepository:
    def __init__(self, database_url: str) -> None:
        self._database_url = database_url

    def ensure_schema(self) -> None:
        with psycopg.connect(self._database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    create table if not exists course_catalog_entries (
                        id uuid primary key,
                        slug text not null unique,
                        title text not null,
                        level text not null,
                        modality text not null,
                        duration_text text not null,
                        learning_summary text not null,
                        market_application text not null,
                        curriculum_text text not null,
                        search_text text not null,
                        source_path text not null,
                        created_at timestamptz not null default now(),
                        updated_at timestamptz not null default now(),
                        constraint course_catalog_entries_level_check
                            check (level in ('graduacao', 'pos-graduacao', 'mba')),
                        constraint course_catalog_entries_modality_check
                            check (modality in ('ead', 'remoto'))
                    );
                    """
                )
                cursor.execute(
                    """
                    create index if not exists ix_course_catalog_entries_level
                        on course_catalog_entries (level);
                    """
                )
                cursor.execute(
                    """
                    create index if not exists ix_course_catalog_entries_modality
                        on course_catalog_entries (modality);
                    """
                )
            connection.commit()

    def upsert_courses(self, courses: tuple[CatalogCourse, ...]) -> int:
        if not courses:
            return 0

        with psycopg.connect(self._database_url) as connection:
            with connection.cursor() as cursor:
                cursor.executemany(
                    """
                    insert into course_catalog_entries (
                        id,
                        slug,
                        title,
                        level,
                        modality,
                        duration_text,
                        learning_summary,
                        market_application,
                        curriculum_text,
                        search_text,
                        source_path
                    ) values (
                        %(id)s,
                        %(slug)s,
                        %(title)s,
                        %(level)s,
                        %(modality)s,
                        %(duration_text)s,
                        %(learning_summary)s,
                        %(market_application)s,
                        %(curriculum_text)s,
                        %(search_text)s,
                        %(source_path)s
                    )
                    on conflict (slug) do update set
                        title = excluded.title,
                        level = excluded.level,
                        modality = excluded.modality,
                        duration_text = excluded.duration_text,
                        learning_summary = excluded.learning_summary,
                        market_application = excluded.market_application,
                        curriculum_text = excluded.curriculum_text,
                        search_text = excluded.search_text,
                        source_path = excluded.source_path,
                        updated_at = now();
                    """,
                    [self._serialize_course(course) for course in courses],
                )
            connection.commit()

        return len(courses)

    def search_courses(
        self,
        query: str | None = None,
        *,
        level: str | None = None,
        modality: str | None = None,
        limit: int = 5,
    ) -> tuple[CatalogCourse, ...]:
        where_clauses: list[str] = []
        params: list[object] = []

        if level is not None:
            where_clauses.append("level = %s")
            params.append(level)
        if modality is not None:
            where_clauses.append("modality = %s")
            params.append(modality)
        if query:
            where_clauses.append("search_text ilike %s")
            params.append(f"%{query}%")

        where_sql = f"where {' and '.join(where_clauses)}" if where_clauses else ""
        sql = f"""
            select
                id,
                slug,
                title,
                level,
                modality,
                duration_text,
                learning_summary,
                market_application,
                curriculum_text,
                source_path
            from course_catalog_entries
            {where_sql}
            order by title asc
            limit %s;
        """
        params.append(max(1, limit))

        with psycopg.connect(self._database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                rows = cursor.fetchall()

        return tuple(self._deserialize_row(row) for row in rows)

    def _serialize_course(self, course: CatalogCourse) -> dict[str, object]:
        return {
            "id": course.id,
            "slug": course.slug,
            "title": course.title,
            "level": course.level,
            "modality": course.modality,
            "duration_text": course.duration_text,
            "learning_summary": course.learning_summary,
            "market_application": course.market_application,
            "curriculum_text": course.curriculum_text,
            "search_text": course.search_text,
            "source_path": course.source_path,
        }

    def _deserialize_row(self, row: Sequence[object]) -> CatalogCourse:
        return CatalogCourse(
            id=row[0],
            slug=row[1],
            title=row[2],
            level=row[3],
            modality=row[4],
            duration_text=row[5],
            learning_summary=row[6],
            market_application=row[7],
            curriculum_items=tuple(str(row[8]).splitlines()),
            source_path=row[9],
        )
