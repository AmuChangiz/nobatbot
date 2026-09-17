from __future__ import annotations

import inspect
from typing import Any, Callable

from bale import Bot as BaleBot
from bale import CallbackQuery as BaleCallbackQuery
from bale import Message as BaleMessage
from bale import User as BaleUser


class UserProxy:
    def __init__(self, user: BaleUser) -> None:
        self._user = user

    @property
    def id(self) -> int:
        return int(self._user.id)

    @property
    def username(self) -> str | None:
        return self._user.username

    @property
    def full_name(self) -> str:
        parts = [self._user.first_name or "", self._user.last_name or ""]
        return " ".join(p for p in parts if p).strip()


class ContactProxy:
    def __init__(self, contact) -> None:
        self._contact = contact

    @property
    def phone_number(self) -> str:
        return str(self._contact.phone_number)


class Message:
    def __init__(self, raw: BaleMessage, bot: "Bot") -> None:
        self._raw = raw
        self._bot = bot
        self.from_user = UserProxy(raw.author) if raw.author else None

    @property
    def text(self) -> str | None:
        return self._raw.content

    @property
    def contact(self):
        return ContactProxy(self._raw.contact) if self._raw.contact else None

    @property
    def chat_id(self) -> int | str:
        return self._raw.chat_id

    @property
    def message_id(self) -> str:
        return self._raw.message_id

    async def answer(self, text: str, reply_markup=None, **kwargs) -> None:
        await self._bot.send_message(self.chat_id, text, reply_markup=reply_markup)

    async def reply(self, text: str, reply_markup=None, **kwargs) -> None:
        await self.answer(text, reply_markup=reply_markup)

    async def delete(self) -> None:
        try:
            await self._raw.delete()
        except Exception:
            pass

    async def edit_text(self, text: str, reply_markup=None, **kwargs) -> None:
        try:
            await self._raw.edit(text, components=reply_markup)
        except Exception:
            await self._bot.send_message(self.chat_id, text, reply_markup=reply_markup)


class CallbackMessageProxy:
    def __init__(self, raw: BaleMessage, bot: "Bot") -> None:
        self._raw = raw
        self._bot = bot
        self.from_user = UserProxy(raw.author) if raw.author else None
        self.chat_id = raw.chat_id
        self.message_id = raw.message_id

    @property
    def text(self) -> str | None:
        return self._raw.content

    async def answer(self, text: str, reply_markup=None, **kwargs) -> None:
        await self._bot.send_message(self.chat_id, text, reply_markup=reply_markup)

    async def edit_text(self, text: str, reply_markup=None, **kwargs) -> None:
        try:
            await self._raw.edit(text, components=reply_markup)
        except Exception:
            await self._bot.send_message(self.chat_id, text, reply_markup=reply_markup)

    async def delete(self) -> None:
        try:
            await self._raw.delete()
        except Exception:
            pass


class CallbackQuery:
    def __init__(self, raw: BaleCallbackQuery, bot: "Bot") -> None:
        self._raw = raw
        self._bot = bot
        self.from_user = UserProxy(raw.from_user) if raw.from_user else None
        self.data = raw.data or ""
        self.message = CallbackMessageProxy(raw.message, bot) if raw.message else None

    async def answer(self, text: str | None = None, show_alert: bool = False) -> None:
        # Bale acks callbacks automatically; optional text ignored if unsupported
        return None


class Bot:
    def __init__(self, token: str) -> None:
        self._bot = BaleBot(token)

    @property
    def inner(self) -> BaleBot:
        return self._bot

    async def send_message(self, chat_id: int | str, text: str, **kwargs) -> None:
        components = kwargs.get("reply_markup") or kwargs.get("components")
        await self._bot.send_message(chat_id, text, components=components)

    async def delete_webhook(self) -> None:
        await self._bot.delete_webhook()

    async def close(self) -> None:
        await self._bot.close()

    def event(self, coro: Callable) -> Callable:
        return self._bot.event(coro)

    def run(self) -> None:
        self._bot.run()

    async def edit_message(
        self,
        chat_id: int | str,
        message_id: str,
        text: str,
        reply_markup=None,
    ) -> None:
        await self._bot.edit_message(chat_id, message_id, text, components=reply_markup)


class ErrorEvent:
    def __init__(self, exception: BaseException, update: Any = None) -> None:
        self.exception = exception
        self.update = update


async def call_handler(handler: Callable, **kwargs: Any) -> Any:
    sig = inspect.signature(handler)
    filtered = {k: v for k, v in kwargs.items() if k in sig.parameters}
    return await handler(**filtered)
