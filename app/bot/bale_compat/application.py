from __future__ import annotations

import inspect
import logging
from typing import Any

from bale import CallbackQuery as BaleCallbackQuery
from bale import Message as BaleMessage

from app.bot.bale_compat.filters import run_filters
from app.bot.bale_compat.fsm import FSMContext, MemoryStorage
from app.bot.bale_compat.router import Router
from app.bot.bale_compat.types import Bot, CallbackQuery, ErrorEvent, Message, call_handler
from app.core.error_reporter import ErrorReporter
from app.services import AdminService, UserService

logger = logging.getLogger(__name__)


class BaleApplication:
    def __init__(
        self,
        bot: Bot,
        router: Router,
        session_factory,
        fsm_storage: MemoryStorage | None = None,
    ) -> None:
        self.bot = bot
        self.router = router
        self.session_factory = session_factory
        self.fsm_storage = fsm_storage or MemoryStorage()
        self._startup: list = []
        self._shutdown: list = []

    def on_startup(self, coro):
        self._startup.append(coro)

    def on_shutdown(self, coro):
        self._shutdown.append(coro)

    async def _build_context(self, user_id: int | None, session) -> dict[str, Any]:
        ctx: dict[str, Any] = {
            "bot": self.bot,
            "session": session,
            "state": FSMContext(self.fsm_storage, user_id) if user_id else None,
        }
        if user_id is not None:
            db_user = await UserService.get_or_create(
                session,
                bale_user_id=user_id,
                full_name=None,
                username=None,
            )
            ctx["db_user"] = db_user
            ctx["is_admin"] = await AdminService.is_admin(session, user_id)
            ctx["db_admin"] = (
                await AdminService.get_admin(session, user_id) if ctx["is_admin"] else None
            )
        return ctx

    async def _run_handler(self, handler, event, ctx: dict) -> None:
        all_filters = ctx.pop("_filters", [])
        for f in all_filters:
            if not await run_filters([f], event, **ctx):
                return
        await call_handler(handler, message=event, callback=event, **ctx)

    async def handle_message(self, raw: BaleMessage) -> None:
        if not raw.author:
            return
        user_id = int(raw.author.id)
        message = Message(raw, self.bot)

        async with self.session_factory() as session:
            try:
                ctx = await self._build_context(user_id, session)
                if raw.author:
                    ctx["db_user"].full_name = message.from_user.full_name
                    ctx["db_user"].username = message.from_user.username

                from app.bot.constants.admin_menu import ADMIN_MENU_BUTTONS

                if (
                    ctx.get("is_admin")
                    and message.text
                    and message.text in ADMIN_MENU_BUTTONS
                    and ctx.get("state") is not None
                ):
                    await ctx["state"].clear()

                for flist, router_filters, handler in self.router.message_handlers:
                    combined = list(router_filters) + list(flist)
                    if not await run_filters(combined, message, **ctx):
                        continue
                    await call_handler(handler, message=message, **ctx)
                    await session.commit()
                    return

                await session.commit()
            except Exception as exc:
                await session.rollback()
                await self._handle_error(exc, raw)

    async def handle_callback(self, raw: BaleCallbackQuery) -> None:
        if not raw.from_user:
            return
        user_id = int(raw.from_user.id)
        callback = CallbackQuery(raw, self.bot)

        async with self.session_factory() as session:
            try:
                ctx = await self._build_context(user_id, session)

                for flist, router_filters, handler in self.router.callback_handlers:
                    combined = list(router_filters) + list(flist)
                    if not await run_filters(combined, callback, **ctx):
                        continue
                    await call_handler(handler, callback=callback, **ctx)
                    await session.commit()
                    return

                await session.commit()
            except Exception as exc:
                await session.rollback()
                await self._handle_error(exc, raw)

    async def _handle_error(self, exc: Exception, update) -> None:
        logger.exception("Handler error: %s", exc)
        await ErrorReporter.report(exc, "پردازش آپدیت")
        event = ErrorEvent(exc, update)
        for handler in self.router.error_handlers:
            try:
                await call_handler(handler, event=event)
            except Exception:
                logger.exception("Error handler failed")

    def register_events(self) -> None:
        bot = self.bot.inner

        @bot.event
        async def on_before_ready():
            await self.bot.delete_webhook()
            for coro in self._startup:
                await coro(self.bot)

        @bot.event
        async def on_message(message: BaleMessage):
            await self.handle_message(message)

        @bot.event
        async def on_callback(callback: BaleCallbackQuery):
            await self.handle_callback(callback)

        @bot.event
        async def on_before_shutdown():
            for coro in self._shutdown:
                await coro(self.bot)

    def run(self) -> None:
        self.register_events()
        self.bot.run()
