from app.engines.prompt.prompt_engine import PromptEngine
from app.integrations.database.repos.in_memory_prompt_registry_repository import InMemoryPromptRegistryRepository
from app.services.prompt.prompt_registry_service import PromptRegistryService


def test_prompt_registry_service_registers_versions_and_activates_selected_one() -> None:
    engine = PromptEngine()
    repository = InMemoryPromptRegistryRepository(prompt_engine=engine)
    service = PromptRegistryService(prompt_registry_repository=repository, prompt_engine=engine)

    created = service.register_prompt("sales-qualification", "template v1", "initial version")
    versioned = service.create_version("sales-qualification", "template v2", "second version")
    second_version_id = versioned.versions[1].id.value
    activated = service.activate_version("sales-qualification", str(second_version_id))

    assert created.active_version() is not None
    assert len(versioned.versions) == 2
    assert activated.active_version() == activated.versions[1]
