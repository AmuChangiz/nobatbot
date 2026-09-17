import logging

from app.bot.bale_compat import Bot

from app.config import get_settings
from app.db.session import get_session_factory
from app.scheduler.runner import scheduled_job
from app.services import AppointmentService
from app.services.notifications import NotificationService

logger = logging.getLogger(__name__)


async def _send_reminders(bot: Bot, hours: int, flag: str) -> int:
    settings = get_settings()
    session_factory = get_session_factory()
    sent = 0

    async with session_factory() as session:
        appointments = await AppointmentService.get_pending_reminders(session, hours)
        for appt in appointments:
            if not NotificationService.is_in_reminder_window(
                appt, hours, settings.reminder_window_minutes
            ):
                continue
            try:
                ok = await NotificationService.send_reminder(bot, appt, hours)
                if ok:
                    if flag == "24h":
                        await AppointmentService.mark_reminder_24h_sent(session, appt.id)
                    else:
                        await AppointmentService.mark_reminder_2h_sent(session, appt.id)
                    sent += 1
            except Exception:
                logger.exception("Reminder failed for appointment %d", appt.id)
        await session.commit()

    if sent:
        logger.info("Sent %d reminders (%dh)", sent, hours)
    return sent


@scheduled_job("یادآوری ۲۴ ساعته")
async def send_24h_reminders_job(bot: Bot) -> int:
    return await _send_reminders(bot, get_settings().reminder_24h_hours, "24h")


@scheduled_job("یادآوری ۲ ساعته")
async def send_2h_reminders_job(bot: Bot) -> int:
    return await _send_reminders(bot, get_settings().reminder_2h_hours, "2h")
