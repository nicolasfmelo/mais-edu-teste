from __future__ import annotations

import re

from app.domain_models.evaluation.models import ExportedConversationMessage

_INJECTION_PATTERNS: list[re.Pattern[str]] = [
    # Instruction override
    re.compile(r"ignore\s+(previous|all|your|the)\s+instructions?", re.IGNORECASE),
    re.compile(r"forget\s+(your|all|previous|the)\s+instructions?", re.IGNORECASE),
    re.compile(r"disregard\s+(all|your|previous|the)?\s*instructions?", re.IGNORECASE),
    re.compile(r"your\s+new\s+instructions?", re.IGNORECASE),
    re.compile(r"override\s+(your|the|all)?\s*instructions?", re.IGNORECASE),
    # Role hijack
    re.compile(r"you\s+are\s+now\s+\w", re.IGNORECASE),
    re.compile(r"act\s+as\s+(if\s+you\s+are|a\s+)", re.IGNORECASE),
    re.compile(r"pretend\s+(you\s+are|to\s+be)", re.IGNORECASE),
    re.compile(r"from\s+now\s+on\s+you\s+(are|will)", re.IGNORECASE),
    re.compile(r"your\s+new\s+(persona|role|identity)", re.IGNORECASE),
    re.compile(r"roleplay\s+as", re.IGNORECASE),
    # Prompt/system extraction
    re.compile(r"(what\s+are|repeat|show|reveal)\s+(your|the)\s+(instructions?|prompt|rules?)", re.IGNORECASE),
    re.compile(r"(print|output|tell\s+me)\s+(your|the)\s+(prompt|system\s+prompt|context)", re.IGNORECASE),
    re.compile(r"(ignore|bypass)\s+(safety|filters?|guidelines?|restrictions?|policies)", re.IGNORECASE),
    # Markup injection
    re.compile(r"\[SYSTEM\]", re.IGNORECASE),
    re.compile(r"<\s*system\s*>", re.IGNORECASE),
    re.compile(r"\[INST\]", re.IGNORECASE),
    re.compile(r"</s>", re.IGNORECASE),
    re.compile(r"###\s*(system|instruction|prompt)", re.IGNORECASE),
    # DAN / jailbreak patterns
    re.compile(r"\bDAN\b"),
    re.compile(r"do\s+anything\s+now", re.IGNORECASE),
    re.compile(r"jailbreak", re.IGNORECASE),
]

_SNIPPET_MAX_LEN = 120


def detect_injection(messages: tuple[ExportedConversationMessage, ...]) -> tuple[bool, list[str]]:
    """Scans user messages for prompt injection patterns.

    Returns (detected, snippets) where snippets are the matching message excerpts.
    """
    snippets: list[str] = []
    for msg in messages:
        if msg.role.lower() != "user":
            continue
        content = msg.content
        for pattern in _INJECTION_PATTERNS:
            if pattern.search(content):
                snippet = content[:_SNIPPET_MAX_LEN]
                if snippet not in snippets:
                    snippets.append(snippet)
                break  # one snippet per message is enough

    return bool(snippets), snippets
