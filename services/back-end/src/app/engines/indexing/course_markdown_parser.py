from __future__ import annotations

from pathlib import Path

from app.domain_models.indexing.models import CatalogCourse


class CourseMarkdownParser:
    _REQUIRED_SECTIONS = (
        "Informacoes gerais",
        "O que voce vai aprender",
        "Onde aplicar no mercado de trabalho",
        "Grade curricular",
    )

    def parse_file(self, file_path: Path, dataset_dir: Path) -> CatalogCourse:
        raw_text = file_path.read_text(encoding="utf-8").strip()
        if not raw_text:
            raise ValueError(f"Dataset file is empty: {file_path}")

        lines = [line.rstrip() for line in raw_text.splitlines()]
        title = self._parse_title(lines, file_path)
        sections = self._parse_sections(lines[1:], file_path)
        info = self._parse_info_section(sections["Informacoes gerais"], file_path)
        curriculum_items = self._parse_curriculum_items(sections["Grade curricular"], file_path)

        return CatalogCourse.from_source(
            slug=file_path.stem,
            title=title,
            level=self._normalize_level(info["nivel"], file_path),
            modality=self._normalize_modality(info["modalidade"], file_path),
            duration_text=info["tempo de formacao"],
            learning_summary=self._join_section(sections["O que voce vai aprender"]),
            market_application=self._join_section(sections["Onde aplicar no mercado de trabalho"]),
            curriculum_items=curriculum_items,
            source_path=file_path.relative_to(dataset_dir),
        )

    def _parse_title(self, lines: list[str], file_path: Path) -> str:
        if not lines or not lines[0].startswith("# "):
            raise ValueError(f"Dataset file must start with a level-1 title: {file_path}")
        title = lines[0][2:].strip()
        if not title:
            raise ValueError(f"Dataset title cannot be empty: {file_path}")
        return title

    def _parse_sections(self, lines: list[str], file_path: Path) -> dict[str, list[str]]:
        sections: dict[str, list[str]] = {}
        current_section: str | None = None

        for line in lines:
            if line.startswith("## "):
                current_section = line[3:].strip()
                sections[current_section] = []
                continue
            if current_section is not None:
                sections[current_section].append(line)

        for section_name in self._REQUIRED_SECTIONS:
            if section_name not in sections:
                raise ValueError(f"Missing required section '{section_name}' in {file_path}")

        return sections

    def _parse_info_section(self, lines: list[str], file_path: Path) -> dict[str, str]:
        info: dict[str, str] = {}

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if not stripped.startswith("- ") or ":" not in stripped:
                raise ValueError(f"Invalid info line '{line}' in {file_path}")
            key, value = stripped[2:].split(":", maxsplit=1)
            info[key.strip().lower()] = value.strip()

        required_keys = ("nivel", "modalidade", "tempo de formacao")
        for key in required_keys:
            if key not in info or not info[key]:
                raise ValueError(f"Missing info field '{key}' in {file_path}")

        return info

    def _parse_curriculum_items(self, lines: list[str], file_path: Path) -> tuple[str, ...]:
        items = tuple(line[2:].strip() for line in lines if line.strip().startswith("- "))
        if not items:
            raise ValueError(f"Grade curricular must contain at least one item in {file_path}")
        return items

    def _join_section(self, lines: list[str]) -> str:
        return " ".join(line.strip() for line in lines if line.strip())

    def _normalize_level(self, value: str, file_path: Path) -> str:
        normalized = value.strip().lower()
        allowed = {"graduacao", "pos-graduacao", "mba"}
        if normalized not in allowed:
            raise ValueError(f"Unsupported level '{value}' in {file_path}")
        return normalized

    def _normalize_modality(self, value: str, file_path: Path) -> str:
        normalized = value.strip().lower()
        allowed = {"ead", "remoto"}
        if normalized not in allowed:
            raise ValueError(f"Unsupported modality '{value}' in {file_path}")
        return normalized
