import asyncio
import logging

from app.bot.bale_compat import Bot, MemoryStorage
from app.bot.bale_compat.application import BaleApplication
from app.bot.handlers import setup_routers
from app.config import get_settings
from app.core.error_reporter import ErrorReporter
from app.core.logging import setup_logging
from app.db.bootstrap import init_database
from app.db.session import dispose_engine, get_engine, get_session_factory
from app.scheduler import setup_scheduler
from app.services import AdminService, ScheduleService, SettingsService

logger = logging.getLogger(__name__)

_scheduler = None


async def on_startup(bot: Bot) -> None:
    global _scheduler
    ErrorReporter.init(bot)

    engine = get_engine()
    await init_database(engine)

    session_factory = get_session_factory()
    async with session_factory() as session:
        await AdminService.bootstrap_superadmins(session)
        await SettingsService.bootstrap_defaults(session)
        removed = await ScheduleService.cleanup_past_without_appointments(session)
        if removed:
            logger.info("Removed %d past schedules on startup", removed)
        await session.commit()

    _scheduler = setup_scheduler(bot)
    _scheduler.start()
    logger.info("Background scheduler started")
    logger.info("Application startup complete")


async def on_shutdown(bot: Bot) -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=True)
        _scheduler = None
    await dispose_engine()
    logger.info("Application shutdown complete")


def main() -> None:
    setup_logging()
    settings = get_settings()

    if settings.database_url.startswith("sqlite"):
        asyncio.run(init_database(get_engine()))

    bot = Bot(token=settings.bot_token)
    session_factory = get_session_factory()
    app = BaleApplication(
        bot=bot,
        router=setup_routers(),
        session_factory=session_factory,
        fsm_storage=MemoryStorage(),
    )

    app.on_startup(on_startup)
    app.on_shutdown(on_shutdown)

    logger.info("Bale bot polling started")
    app.run()


if __name__ == "__main__":
    main()
