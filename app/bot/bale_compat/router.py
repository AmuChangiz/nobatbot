from __future__ import annotations

from typing import Callable

from app.bot.bale_compat.filters import normalize_callback_filters, normalize_message_filters


class Router:
    def __init__(self, name: str = __name__) -> None:
        self.name = name
        self.message_handlers: list[tuple[tuple, list, Callable]] = []
        self.callback_handlers: list[tuple[tuple, list, Callable]] = []
        self._message_filters: list = []
        self._callback_filters: list = []
        self.error_handlers: list[Callable] = []
        self.message = _MessageRouter(self)
        self.callback_query = _CallbackRouter(self)

    def include_router(self, other: "Router") -> None:
        self.message_handlers.extend(other.message_handlers)
        self.callback_handlers.extend(other.callback_handlers)
        self.error_handlers.extend(other.error_handlers)

    def errors(self):
        def decorator(func: Callable):
            self.error_handlers.append(func)
            return func
        return decorator


class _MessageRouter:
    def __init__(self, router: Router) -> None:
        self._router = router

    def filter(self, *filters):
        self._router._message_filters.extend(filters)
        return self._router

    def __call__(self, *filters):
        def decorator(func: Callable):
            flist = normalize_message_filters(*filters)
            self._router.message_handlers.append(
                (tuple(flist), list(self._router._message_filters), func)
            )
            return func
        return decorator


class _CallbackRouter:
    def __init__(self, router: Router) -> None:
        self._router = router

    def filter(self, *filters):
        self._router._callback_filters.extend(filters)
        return self._router

    def __call__(self, *filters):
        def decorator(func: Callable):
            flist = normalize_callback_filters(*filters)
            self._router.callback_handlers.append(
                (tuple(flist), list(self._router._callback_filters), func)
            )
            return func
        return decorator
