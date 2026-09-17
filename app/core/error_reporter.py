import logging
import traceback
from typing import TYPE_CHECKING

from app.bot.texts import fa as t
from app.config import get_settings
from app.db.session import get_session_factory
from app.services import AdminService

if TYPE_CHECKING:
    from app.bot.bale_compat import Bot

logger = logging.getLogger(__name__)


class ErrorReporter:
    _bot: "Bot | None" = None

    @classmethod
    def init(cls, bot: "Bot") -> None:
        cls._bot = bot

    @classmethod
    async def report(cls, error: BaseException, context: str) -> None:
        settings = get_settings()
        error_text = str(error)[:500]
        tb = traceback.format_exc()[-800:]

        logger.error("Error in %s: %s\n%s", context, error, tb)

        if not settings.error_notify_admins or cls._bot is None:
            return

        message = t.NOTIFY_ADMIN_ERROR.format(context=context, error=error_text)
        session_factory = get_session_factory()
        async with session_factory() as session:
            try:
                admins = await AdminService.list_admins(session)
                for admin in admins:
                    if admin.is_superadmin:
                        try:
                            await cls._bot.send_message(admin.bale_user_id, message)
                        except Exception:
                            logger.exception(
                                "Failed to notify superadmin %d about error", admin.bale_user_id
                            )
            except Exception:
                logger.exception("Failed to load admins for error notification")
