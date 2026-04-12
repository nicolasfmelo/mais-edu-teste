from __future__ import annotations

from uuid import UUID

from app.domain_models.common.ids import SessionId
from app.domain_models.evaluation.models import (
    BehaviorChange,
    ClosingSignal,
    EvaluationEvidence,
    SatisfactionClass,
    SessionEvaluation,
    TokenUsage,
)

_SATISFACTION_MAP = {"bom": SatisfactionClass.GOOD, "neutro": SatisfactionClass.NEUTRAL, "ruim": SatisfactionClass.BAD}
_BEHAVIOR_MAP = {
    "positiva": BehaviorChange.POSITIVE,
    "neutra": BehaviorChange.NEUTRAL,
    "negativa": BehaviorChange.NEGATIVE,
}
_CLOSING_MAP = {
    "positivo": ClosingSignal.POSITIVE,
    "neutro": ClosingSignal.NEUTRAL,
    "negativo": ClosingSignal.NEGATIVE,
}


def parse_session_evaluation(
    session_id_str: str,
    parsed: dict,
    prompt_tokens: int | None = None,
    completion_tokens: int | None = None,
    heuristic_injection_detected: bool = False,
    heuristic_injection_snippets: list[str] | None = None,
) -> SessionEvaluation:
    """Maps a parsed LLM JSON dict into a SessionEvaluation domain model.

    Combines heuristic injection signals with the LLM semantic detection using OR logic.
    Applies safe fallbacks for every field so a partial LLM response never raises.
    """
    satisfaction_raw = str(parsed.get("satisfacao", "neutro")).lower()
    satisfaction = _SATISFACTION_MAP.get(satisfaction_raw, SatisfactionClass.NEUTRAL)

    behavior_raw = str(parsed.get("mudanca_comportamental", "neutra")).lower()
    behavior = _BEHAVIOR_MAP.get(behavior_raw, BehaviorChange.NEUTRAL)

    closing_raw = str(parsed.get("sinal_fechamento", "neutro")).lower()
    closing = _CLOSING_MAP.get(closing_raw, ClosingSignal.NEUTRAL)

    effort = _clamp(int(parsed.get("esforco_1_5", 3)), 1, 5)
    understanding = _clamp(int(parsed.get("entendimento_objetivo_0_2", 1)), 0, 2)
    resolution = _clamp(int(parsed.get("resolucao_0_2", 1)), 0, 2)

    evidences = tuple(
        EvaluationEvidence(snippet=str(e)[:120])
        for e in (parsed.get("evidencias") or [])
        if e
    )

    token_usage: TokenUsage | None = None
    if prompt_tokens is not None and completion_tokens is not None:
        token_usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )

    llm_injection = bool(parsed.get("injection_attempt", False))
    llm_evidence_raw = parsed.get("injection_evidence")
    llm_evidence = str(llm_evidence_raw)[:120] if llm_evidence_raw and llm_evidence_raw != "null" else None

    injection_detected = heuristic_injection_detected or llm_injection
    all_snippets: list[str] = list(heuristic_injection_snippets or [])
    if llm_evidence and llm_evidence not in all_snippets:
        all_snippets.append(llm_evidence)

    return SessionEvaluation(
        session_id=SessionId(value=UUID(session_id_str)),
        satisfaction=satisfaction,
        effort_score=effort,
        understanding_score=understanding,
        resolution_score=resolution,
        evidences=evidences,
        objetivo_cliente=str(parsed.get("objetivo_cliente", "")),
        mudanca_comportamental=behavior,
        sinal_fechamento=closing,
        token_usage=token_usage,
        prompt_injection_detected=injection_detected,
        injection_snippets=tuple(all_snippets),
    )


def _clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))
