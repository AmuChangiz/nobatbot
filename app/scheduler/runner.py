import functools
import logging
from collections.abc import Callable, Coroutine
from typing import Any, ParamSpec, TypeVar

from app.core.error_reporter import ErrorReporter

P = ParamSpec("P")
R = TypeVar("R")

logger = logging.getLogger(__name__)


def scheduled_job(name: str) -> Callable[[Callable[P, Coroutine[Any, Any, R]]], Callable[P, Coroutine[Any, Any, R]]]:
    def decorator(func: Callable[P, Coroutine[Any, Any, R]]) -> Callable[P, Coroutine[Any, Any, R]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
            logger.info("Starting job: %s", name)
            try:
                result = await func(*args, **kwargs)
                logger.info("Completed job: %s", name)
                return result
            except Exception as exc:
                logger.exception("Job failed: %s", name)
                await ErrorReporter.report(exc, f"کار پس‌زمینه: {name}")
                return None

        wrapper.__job_name__ = name  # type: ignore[attr-defined]
        return wrapper

    return decorator
