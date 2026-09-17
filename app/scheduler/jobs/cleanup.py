import logging

from app.bot.bale_compat import Bot
from sqlalchemy import delete

from app.db.models import SlotLock
from app.db.session import get_session_factory
from app.scheduler.runner import scheduled_job
from app.services import ScheduleService, SlotService
from app.utils import now_db

logger = logging.getLogger(__name__)


@scheduled_job("پاکسازی قفل اسلات")
async def cleanup_expired_locks_job(bot: Bot) -> int:
    session_factory = get_session_factory()
    async with session_factory() as session:
        count = await SlotService.cleanup_expired_locks(session)
        await session.commit()
        if count:
            logger.info("Removed %d expired slot locks", count)
        return count


@scheduled_job("پاکسازی شبانه")
async def cleanup_all_job(bot: Bot) -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        lock_result = await session.execute(
            delete(SlotLock)
            .where(SlotLock.locked_until <= now_db())
            .execution_options(synchronize_session=False)
        )
        lock_count = lock_result.rowcount or 0
        schedule_count = await ScheduleService.cleanup_past_without_appointments(session)
        await session.commit()
        logger.info(
            "Nightly cleanup: %d stale locks, %d past schedules removed",
            lock_count,
            schedule_count,
        )
