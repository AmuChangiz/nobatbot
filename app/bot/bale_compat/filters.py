from __future__ import annotations

import inspect
from typing import Any, Callable

from app.bot.bale_compat.fsm import State
from app.bot.bale_compat.types import CallbackQuery, Message


class CommandStart:
    async def __call__(self, message: Message, **kwargs: Any) -> bool:
        if not message.text:
            return False
        cmd = message.text.split()[0].split("@")[0]
        return cmd in {"/start", "/Start"}


class Command:
    def __init__(self, command: str) -> None:
        self.command = command if command.startswith("/") else f"/{command}"

    async def __call__(self, message: Message, **kwargs: Any) -> bool:
        if not message.text:
            return False
        cmd = message.text.split()[0].split("@")[0]
        return cmd.lower() == self.command.lower()


class StateFilter:
    def __init__(self, state: State) -> None:
        self.state = state

    async def __call__(self, **kwargs: Any) -> bool:
        fsm = kwargs.get("state")
        if fsm is None:
            return False
        current = await fsm.get_state()
        return current == self.state.state


class _TextEqualsFilter:
    def __init__(self, text: str) -> None:
        self.text = text

    async def __call__(self, message: Message, **kwargs: Any) -> bool:
        return message.text == self.text


class _HasTextFilter:
    async def __call__(self, message: Message, **kwargs: Any) -> bool:
        return bool(message.text)


class _TextFilter:
    def __eq__(self, other: str) -> _TextEqualsFilter:
        return _TextEqualsFilter(other)

    async def __call__(self, message: Message, **kwargs: Any) -> bool:
        return bool(message.text)


class _ContactFilter:
    async def __call__(self, message: Message, **kwargs: Any) -> bool:
        return message.contact is not None


class DataStartswithFilter:
    def __init__(self, prefix: str) -> None:
        self.prefix = prefix

    async def __call__(self, callback: CallbackQuery = None, **kwargs: Any) -> bool:
        if callback is None:
            return False
        return callback.data.startswith(self.prefix)


class DataEqualsFilter:
    def __init__(self, value: str) -> None:
        self.value = value

    async def __call__(self, callback: CallbackQuery = None, **kwargs: Any) -> bool:
        if callback is None:
            return False
        return callback.data == self.value


class _CallbackDataFilter:
    def startswith(self, prefix: str) -> DataStartswithFilter:
        return DataStartswithFilter(prefix)

    def __eq__(self, other: str) -> DataEqualsFilter:
        return DataEqualsFilter(other)


class F:
    text = _TextFilter()
    contact = _ContactFilter()
    data = _CallbackDataFilter()


def normalize_message_filters(*filters) -> list:
    result = []
    for f in filters:
        if isinstance(f, State):
            result.append(StateFilter(f))
        else:
            result.append(f)
    return result


def normalize_callback_filters(*filters) -> list:
    result = []
    for f in filters:
        if isinstance(f, State):
            result.append(StateFilter(f))
        elif isinstance(f, str):
            if f.startswith("data:"):
                result.append(DataStartswithFilter(f[5:]))
            else:
                result.append(DataEqualsFilter(f))
        else:
            result.append(f)
    return result


async def _call_filter(f: Any, event: Any, ctx: dict[str, Any]) -> bool:
    if isinstance(f, StateFilter):
        return await f(**ctx)
    if isinstance(f, (DataStartswithFilter, DataEqualsFilter)):
        return await f(callback=event, **ctx)
    if isinstance(f, (_ContactFilter, _TextEqualsFilter, _HasTextFilter, Command, CommandStart)):
        return await f(event, **ctx)
    if callable(f):
        sig = inspect.signature(f)
        params = sig.parameters
        if "event" in params:
            return await f(event, **{k: v for k, v in ctx.items() if k in params})
        if "message" in params and isinstance(event, Message):
            return await f(event, **{k: v for k, v in ctx.items() if k in params})
        if "callback" in params and isinstance(event, CallbackQuery):
            return await f(event, **{k: v for k, v in ctx.items() if k in params})
        merged = {"event": event, **ctx}
        return await f(**{k: v for k, v in merged.items() if k in params})
    return True


async def run_filters(filters: list, event: Any, **ctx) -> bool:
    for f in filters:
        if not await _call_filter(f, event, ctx):
            return False
    return True
