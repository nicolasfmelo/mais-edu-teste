from pathlib import Path

from app.engines.prompt.prompt_engine import PromptEngine
from app.integrations.database.repos.sqlalchemy_prompt_registry_repository import SQLAlchemyPromptRegistryRepository
from app.integrations.database.sqlalchemy_database import SQLAlchemyDatabase
from app.services.prompt.agent_prompt_service import (
    AgentPromptService,
    CHAT_AGENT_DEFAULT_PROMPT,
    CHAT_AGENT_PROMPT_KEY,
    NPS_AGENT_DEFAULT_PROMPT,
    NPS_AGENT_PROMPT_KEY,
)
from app.services.prompt.prompt_registry_service import PromptRegistryService


def test_agent_prompt_service_resolves_active_prompts_for_chat_and_nps(tmp_path: Path) -> None:
    database = SQLAlchemyDatabase(f"sqlite+pysqlite:///{tmp_path / 'agent-prompts.db'}")
    database.create_schema()
    prompt_engine = PromptEngine()
    repository = SQLAlchemyPromptRegistryRepository(database=database)
    prompt_registry_service = PromptRegistryService(
        prompt_registry_repository=repository,
        prompt_engine=prompt_engine,
    )
    prompt_registry_service.register_prompt(
        CHAT_AGENT_PROMPT_KEY,
        "chat prompt",
        "chat initial",
    )
    prompt_registry_service.register_prompt(
        NPS_AGENT_PROMPT_KEY,
        "nps prompt",
        "nps initial",
    )

    service = AgentPromptService(prompt_registry_service=prompt_registry_service)

    assert service.get_chat_system_prompt() == "chat prompt"
    assert service.get_nps_system_prompt() == "nps prompt"


def test_agent_prompt_service_seeds_default_baseline_prompts_once(tmp_path: Path) -> None:
    database = SQLAlchemyDatabase(f"sqlite+pysqlite:///{tmp_path / 'agent-prompts-defaults.db'}")
    database.create_schema()
    prompt_engine = PromptEngine()
    repository = SQLAlchemyPromptRegistryRepository(database=database)
    prompt_registry_service = PromptRegistryService(
        prompt_registry_repository=repository,
        prompt_engine=prompt_engine,
    )
    service = AgentPromptService(prompt_registry_service=prompt_registry_service)

    service.ensure_default_prompts()
    service.ensure_default_prompts()

    chat_entry = prompt_registry_service.get_prompt(CHAT_AGENT_PROMPT_KEY)
    nps_entry = prompt_registry_service.get_prompt(NPS_AGENT_PROMPT_KEY)

    assert len(chat_entry.versions) == 1
    assert len(nps_entry.versions) == 1
    assert chat_entry.versions[0].template == CHAT_AGENT_DEFAULT_PROMPT
    assert nps_entry.versions[0].template == NPS_AGENT_DEFAULT_PROMPT
