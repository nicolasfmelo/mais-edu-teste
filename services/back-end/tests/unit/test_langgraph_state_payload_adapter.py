from dataclasses import dataclass

import pytest

from app.integrations.langgraph.state_payload_adapter import LangGraphStatePayloadAdapter


@dataclass(frozen=True)
class _FakeState:
    value: int


def test_langgraph_state_payload_adapter_wraps_typed_state_handlers() -> None:
    adapter = LangGraphStatePayloadAdapter(_FakeState, "fake state")

    def increment(state: _FakeState) -> _FakeState:
        return _FakeState(value=state.value + 1)

    payload = adapter.wrap_node(increment)(adapter.to_payload(_FakeState(value=1)))

    assert adapter.from_payload(payload) == _FakeState(value=2)


def test_langgraph_state_payload_adapter_rejects_invalid_payload() -> None:
    adapter = LangGraphStatePayloadAdapter(_FakeState, "fake state")

    with pytest.raises(TypeError):
        adapter.from_payload({"state": "wrong"})
