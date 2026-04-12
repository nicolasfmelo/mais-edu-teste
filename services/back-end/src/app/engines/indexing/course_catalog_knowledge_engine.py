from __future__ import annotations

from app.domain_models.common.ids import DocumentId
from app.domain_models.indexing.models import CatalogCourse
from app.domain_models.rag.models import KnowledgeDocument


class CourseCatalogKnowledgeEngine:
    def build_document(self, course: CatalogCourse) -> KnowledgeDocument:
        return KnowledgeDocument(
            id=DocumentId(value=course.id),
            title=course.title,
            content=self._render_content(course),
            source=course.source_path,
        )

    def _render_content(self, course: CatalogCourse) -> str:
        return (
            f"Curso: {course.title}\n"
            f"Nivel: {course.level}\n"
            f"Modalidade: {course.modality}\n"
            f"Duracao: {course.duration_text}\n"
            f"O que voce vai aprender: {course.learning_summary}\n"
            f"Aplicacao no mercado: {course.market_application}\n"
            f"Grade curricular: {', '.join(course.curriculum_items)}"
        )
