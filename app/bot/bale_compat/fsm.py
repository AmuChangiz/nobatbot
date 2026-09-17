from __future__ import annotations

from typing import Any


class State:
    state: str | None = None

    def __set_name__(self, owner: type, name: str) -> None:
        self.state = f"{owner.__name__}:{name}"


class StatesGroup:
    pass


class FSMContext:
    def __init__(self, storage: "MemoryStorage", user_id: int) -> None:
        self._storage = storage
        self._user_id = user_id

    async def get_state(self) -> str | None:
        return self._storage.get_state(self._user_id)

    async def set_state(self, state: State | str | None) -> None:
        if state is None:
            self._storage.set_state(self._user_id, None)
        elif isinstance(state, State):
            self._storage.set_state(self._user_id, state.state)
        else:
            self._storage.set_state(self._user_id, state)

    async def clear(self) -> None:
        self._storage.clear(self._user_id)

    async def get_data(self) -> dict[str, Any]:
        return self._storage.get_data(self._user_id)

    async def update_data(self, **kwargs: Any) -> None:
        self._storage.update_data(self._user_id, **kwargs)

    async def set_data(self, data: dict[str, Any]) -> None:
        self._storage.set_data(self._user_id, data)


class MemoryStorage:
    def __init__(self) -> None:
        self._states: dict[int, str | None] = {}
        self._data: dict[int, dict[str, Any]] = {}

    def get_state(self, user_id: int) -> str | None:
        return self._states.get(user_id)

    def set_state(self, user_id: int, state: str | None) -> None:
        self._states[user_id] = state

    def get_data(self, user_id: int) -> dict[str, Any]:
        return dict(self._data.get(user_id, {}))

    def set_data(self, user_id: int, data: dict[str, Any]) -> None:
        self._data[user_id] = dict(data)

    def update_data(self, user_id: int, **kwargs: Any) -> None:
        if user_id not in self._data:
            self._data[user_id] = {}
        self._data[user_id].update(kwargs)

    def clear(self, user_id: int) -> None:
        self._states.pop(user_id, None)
        self._data.pop(user_id, None)
