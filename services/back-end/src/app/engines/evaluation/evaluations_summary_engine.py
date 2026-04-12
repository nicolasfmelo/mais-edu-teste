from __future__ import annotations

from app.domain_models.evaluation.models import EvaluationsSummary, SatisfactionClass, SessionEvaluation


class EvaluationsSummaryEngine:
    """Aggregates a collection of session evaluations into a summary."""

    def build_summary(self, evaluations: tuple[SessionEvaluation, ...]) -> EvaluationsSummary:
        total = len(evaluations)
        if total == 0:
            return EvaluationsSummary(
                total_evaluated=0,
                count_bom=0,
                count_neutro=0,
                count_ruim=0,
                pct_bom=0.0,
                pct_neutro=0.0,
                pct_ruim=0.0,
                indice_ia_operadora=0.0,
                avg_effort=0.0,
                avg_understanding=0.0,
                avg_resolution=0.0,
            )

        count_bom = sum(1 for e in evaluations if e.satisfaction == SatisfactionClass.GOOD)
        count_neutro = sum(1 for e in evaluations if e.satisfaction == SatisfactionClass.NEUTRAL)
        count_ruim = sum(1 for e in evaluations if e.satisfaction == SatisfactionClass.BAD)

        pct_bom = round(count_bom / total * 100, 1)
        pct_neutro = round(count_neutro / total * 100, 1)
        pct_ruim = round(count_ruim / total * 100, 1)

        return EvaluationsSummary(
            total_evaluated=total,
            count_bom=count_bom,
            count_neutro=count_neutro,
            count_ruim=count_ruim,
            pct_bom=pct_bom,
            pct_neutro=pct_neutro,
            pct_ruim=pct_ruim,
            indice_ia_operadora=round(pct_bom - pct_ruim, 1),
            avg_effort=round(sum(e.effort_score for e in evaluations) / total, 2),
            avg_understanding=round(sum(e.understanding_score for e in evaluations) / total, 2),
            avg_resolution=round(sum(e.resolution_score for e in evaluations) / total, 2),
        )
