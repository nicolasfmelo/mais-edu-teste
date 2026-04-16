from pathlib import Path

import pytest

from app.engines.prompt.prompt_engine import PromptEngine
from app.domain_models.prompt.exceptions import PromptAlreadyExistsError
from app.integrations.database.repos.sqlalchemy_prompt_registry_repository import SQLAlchemyPromptRegistryRepository
from app.integrations.database.sqlalchemy_database import SQLAlchemyDatabase
from app.services.prompt.prompt_registry_service import PromptRegistryService


def test_prompt_registry_service_registers_versions_and_activates_selected_one(tmp_path: Path) -> None:
    database = SQLAlchemyDatabase(f"sqlite+pysqlite:///{tmp_path / 'service_prompt.db'}")
    database.create_schema()
    engine = PromptEngine()
    repository = SQLAlchemyPromptRegistryRepository(database=database)
    service = PromptRegistryService(prompt_registry_repository=repository, prompt_engine=engine)

    created = service.register_prompt("sales-qualification", "template v1", "initial version")
    versioned = service.create_version("sales-qualification", "template v2", "second version")
    second_version_id = versioned.versions[1].id.value
    activated = service.activate_version("sales-qualification", str(second_version_id))

    assert created.active_version() is not None
    assert len(versioned.versions) == 2
    assert activated.active_version() == activated.versions[1]


def test_prompt_registry_service_ensure_prompt_is_idempotent(tmp_path: Path) -> None:
    database = SQLAlchemyDatabase(f"sqlite+pysqlite:///{tmp_path / 'service_prompt_ensure.db'}")
    database.create_schema()
    engine = PromptEngine()
    repository = SQLAlchemyPromptRegistryRepository(database=database)
    service = PromptRegistryService(prompt_registry_repository=repository, prompt_engine=engine)

    first = service.ensure_prompt("sales-qualification", "template v1", "initial version")
    second = service.ensure_prompt("sales-qualification", "template v1", "initial version")

    assert len(first.versions) == 1
    assert len(second.versions) == 1
    assert second.active_version() is not None


def test_prompt_registry_service_register_prompt_keeps_conflict_behavior(tmp_path: Path) -> None:
    database = SQLAlchemyDatabase(f"sqlite+pysqlite:///{tmp_path / 'service_prompt_conflict.db'}")
    database.create_schema()
    engine = PromptEngine()
    repository = SQLAlchemyPromptRegistryRepository(database=database)
    service = PromptRegistryService(prompt_registry_repository=repository, prompt_engine=engine)

    service.register_prompt("sales-qualification", "template v1", "initial version")

    with pytest.raises(PromptAlreadyExistsError):
        service.register_prompt("sales-qualification", "template v1", "initial version")
