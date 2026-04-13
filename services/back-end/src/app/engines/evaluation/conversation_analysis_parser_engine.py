from __future__ import annotations

from app.domain_models.common.ids import SessionId
from app.domain_models.evaluation.models import (
    ParsedAnalysisResponse,
    SessionEvaluation,
    TokenUsage,
)


def parse_session_evaluation(
    session_id: SessionId,
    parsed: ParsedAnalysisResponse,
    prompt_tokens: int | None = None,
    completion_tokens: int | None = None,
    heuristic_injection_detected: bool = False,
    heuristic_injection_snippets: list[str] | None = None,
) -> SessionEvaluation:
    """Maps a parsed LLM response into a SessionEvaluation domain model.

    Combines heuristic injection signals with the LLM semantic detection using OR logic.
    Applies safe fallbacks for every field so a partial LLM response never raises.
    """
    token_usage: TokenUsage | None = None
    if prompt_tokens is not None and completion_tokens is not None:
        token_usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )

    injection_detected = heuristic_injection_detected or parsed.injection_attempt
    all_snippets: list[str] = list(heuristic_injection_snippets or [])
    if parsed.injection_evidence and parsed.injection_evidence not in all_snippets:
        all_snippets.append(parsed.injection_evidence)

    return SessionEvaluation(
        session_id=session_id,
        satisfaction=parsed.satisfaction,
        effort_score=parsed.effort_score,
        understanding_score=parsed.understanding_score,
        resolution_score=parsed.resolution_score,
        evidences=parsed.evidences,
        objetivo_cliente=parsed.objetivo_cliente,
        mudanca_comportamental=parsed.behavior_change,
        sinal_fechamento=parsed.closing_signal,
        token_usage=token_usage,
        prompt_injection_detected=injection_detected,
        injection_snippets=tuple(all_snippets),
    )
