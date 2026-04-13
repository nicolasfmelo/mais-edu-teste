from __future__ import annotations

from typing import Callable, Generic, TypeVar


StateT = TypeVar("StateT")


class LangGraphStatePayloadAdapter(Generic[StateT]):
    def __init__(self, state_type: type[StateT], state_name: str) -> None:
        self._state_type = state_type
        self._state_name = state_name

    def to_payload(self, state: StateT) -> dict[str, object]:
        return {"state": state}

    def from_payload(self, payload: dict[str, object]) -> StateT:
        state = payload["state"]
        if not isinstance(state, self._state_type):
            raise TypeError(f"Unexpected {self._state_name} payload.")
        return state

    def wrap_node(self, handler: Callable[[StateT], StateT]) -> Callable[[dict[str, object]], dict[str, object]]:
        def wrapped(payload: dict[str, object]) -> dict[str, object]:
            state = self.from_payload(payload)
            return self.to_payload(handler(state))

        return wrapped
