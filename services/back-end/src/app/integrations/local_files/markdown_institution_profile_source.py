from __future__ import annotations

import re
from pathlib import Path

from app.domain_models.agent.models import InstitutionProfile
from app.domain_models.common.exceptions import InstitutionProfileUnavailableError


class MarkdownInstitutionProfileSource:
    def __init__(self, profile_path: Path) -> None:
        self._profile_path = profile_path

    def load(self) -> InstitutionProfile:
        try:
            markdown = self._profile_path.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise InstitutionProfileUnavailableError(
                f"Unable to load institution profile from {self._profile_path}."
            ) from exc

        try:
            return InstitutionProfile(
                institution_name=self._extract_institution_name(markdown),
                agent_name=self._extract_agent_name(markdown),
                presentation_example=self._extract_presentation_example(markdown),
                briefing_markdown=markdown,
            )
        except ValueError as exc:
            raise InstitutionProfileUnavailableError(
                f"Unable to parse institution profile from {self._profile_path}."
            ) from exc

    def _extract_institution_name(self, markdown: str) -> str:
        match = re.search(r"^#\s+(.+)$", markdown, flags=re.MULTILINE)
        if match is None:
            raise ValueError("Missing institution heading.")
        return match.group(1).strip()

    def _extract_agent_name(self, markdown: str) -> str:
        match = re.search(r"### Nome da agente\s+\n+\*\*(.+?)\*\*", markdown, flags=re.MULTILINE)
        if match is None:
            raise ValueError("Missing agent name section.")
        return match.group(1).strip()

    def _extract_presentation_example(self, markdown: str) -> str:
        match = re.search(r"^>\s+(.+)$", markdown, flags=re.MULTILINE)
        if match is None:
            raise ValueError("Missing presentation example.")
        return match.group(1).strip()
