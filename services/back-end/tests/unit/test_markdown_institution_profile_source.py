from pathlib import Path

from app.integrations.local_files.markdown_institution_profile_source import MarkdownInstitutionProfileSource


def test_markdown_institution_profile_source_loads_agent_and_institution_details(tmp_path: Path) -> None:
    profile_path = tmp_path / "institution-profile.md"
    profile_path.write_text(
        "# Instituto Horizonte Digital\n\n"
        "### Nome da agente\n\n"
        "**Clara**\n\n"
        "### Como Clara deve se apresentar\n\n"
        "> Oi, eu sou a Clara, assistente virtual do Instituto Horizonte Digital.\n",
        encoding="utf-8",
    )

    profile = MarkdownInstitutionProfileSource(profile_path=profile_path).load()

    assert profile.institution_name == "Instituto Horizonte Digital"
    assert profile.agent_name == "Clara"
    assert "assistente virtual" in profile.presentation_example
