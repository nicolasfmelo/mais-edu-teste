from __future__ import annotations

import json
import re

from app.domain_models.evaluation.models import (
    BehaviorChange,
    ClosingSignal,
    EvaluationEvidence,
    ExportedConversationSession,
    ParsedAnalysisResponse,
    SatisfactionClass,
)


_ANALYSIS_SCHEMA = """
{
  "session_id": "<string>",
  "objetivo_cliente": "<string — objetivo principal inferido>",
  "satisfacao": "<ruim | neutro | bom>",
  "satisfacao_label": <1 | 2 | 3>,
  "esforco_1_5": <1 | 2 | 3 | 4 | 5>,
  "entendimento_objetivo_0_2": <0 | 1 | 2>,
  "resolucao_0_2": <0 | 1 | 2>,
  "mudanca_comportamental": "<positiva | neutra | negativa>",
  "sinal_fechamento": "<positivo | neutro | negativo>",
  "evidencias": ["<trecho curto da conversa>", ...],
  "injection_attempt": <true | false>,
  "injection_evidence": "<trecho curto que indica tentativa de injeção, ou null>"
}
"""

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


def build_analysis_prompt(session: ExportedConversationSession, system_prompt: str) -> str:
    """Builds the full LLM prompt for a single session analysis."""
    conversation_text = _format_conversation(session)
    session_id = str(session.session_id)
    return (
        f"{system_prompt.strip()}\n\n"
        f"JSON esperado:\n{_ANALYSIS_SCHEMA}\n\n"
        f"Session ID: {session_id}\n\n"
        f"Conversa:\n{conversation_text}"
    )


def parse_analysis_response(raw: str) -> ParsedAnalysisResponse:
    """Extracts and parses the JSON object from the LLM raw text response."""
    raw = raw.strip()
    json_match = re.search(r"\{[\s\S]+\}", raw)
    if not json_match:
        raise ValueError(f"No JSON object found in LLM response: {raw[:200]!r}")
    payload = json.loads(json_match.group())
    if not isinstance(payload, dict):
        raise ValueError("Expected a JSON object in LLM response.")

    satisfaction_raw = str(payload.get("satisfacao", "neutro")).lower()
    behavior_raw = str(payload.get("mudanca_comportamental", "neutra")).lower()
    closing_raw = str(payload.get("sinal_fechamento", "neutro")).lower()
    injection_evidence_raw = payload.get("injection_evidence")

    return ParsedAnalysisResponse(
        objetivo_cliente=str(payload.get("objetivo_cliente", "")),
        satisfaction=_SATISFACTION_MAP.get(satisfaction_raw, SatisfactionClass.NEUTRAL),
        effort_score=_clamp(int(payload.get("esforco_1_5", 3)), 1, 5),
        understanding_score=_clamp(int(payload.get("entendimento_objetivo_0_2", 1)), 0, 2),
        resolution_score=_clamp(int(payload.get("resolucao_0_2", 1)), 0, 2),
        behavior_change=_BEHAVIOR_MAP.get(behavior_raw, BehaviorChange.NEUTRAL),
        closing_signal=_CLOSING_MAP.get(closing_raw, ClosingSignal.NEUTRAL),
        evidences=tuple(
            EvaluationEvidence(snippet=str(evidence)[:120])
            for evidence in (payload.get("evidencias") or [])
            if evidence
        ),
        injection_attempt=bool(payload.get("injection_attempt", False)),
        injection_evidence=(
            str(injection_evidence_raw)[:120]
            if injection_evidence_raw and injection_evidence_raw != "null"
            else None
        ),
    )


def _format_conversation(session: ExportedConversationSession) -> str:
    lines = []
    for message in session.messages:
        lines.append(f"[{message.role.upper()}]: {message.content}")
    return "\n".join(lines)


def _clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))
