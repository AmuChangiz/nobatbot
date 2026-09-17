import logging

from app.bot.bale_compat import ErrorEvent, Router
from app.core.error_reporter import ErrorReporter

logger = logging.getLogger(__name__)

router = Router(name="errors")


@router.errors()
async def user_error_handler(event: ErrorEvent) -> None:
    exc = event.exception
    logger.exception("Unhandled error: %s", exc)
    await ErrorReporter.report(exc, "پردازش پیام کاربر")
