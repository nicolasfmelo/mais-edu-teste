from app.domain_models.prompt.models import PromptActivation, PromptKey, PromptRegistryEntry, PromptVersion, PromptVersionId
from app.engines.prompt.prompt_engine import PromptEngine


def test_prompt_engine_normalizes_key() -> None:
    engine = PromptEngine()

    normalized = engine.normalize_key(" Sales_Qualification ")

    assert normalized.value == "sales-qualification"


def test_prompt_engine_activates_selected_version() -> None:
    engine = PromptEngine()
    first_version = PromptVersion(
        id=PromptVersionId.new(),
        version_number=1,
        template="v1",
        description="first",
        is_active=True,
    )
    second_version = PromptVersion(
        id=PromptVersionId.new(),
        version_number=2,
        template="v2",
        description="second",
        is_active=False,
    )
    entry = PromptRegistryEntry(key=PromptKey("sales"), versions=(first_version, second_version))

    updated = engine.activate_version(
        entry,
        PromptActivation(key=entry.key, version_id=second_version.id),
    )

    assert updated.active_version() == updated.versions[1]
    assert updated.versions[0].is_active is False
