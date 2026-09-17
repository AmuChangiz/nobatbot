import logging

from app.bot.bale_compat import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.config import get_settings
from app.scheduler.jobs.cleanup import cleanup_all_job, cleanup_expired_locks_job
from app.scheduler.jobs.reminders import send_2h_reminders_job, send_24h_reminders_job
from app.scheduler.jobs.reports import daily_report_job, generate_statistics_job

logger = logging.getLogger(__name__)


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    settings = get_settings()
    scheduler = AsyncIOScheduler(timezone=settings.timezone)

    scheduler.add_job(
        cleanup_expired_locks_job,
        trigger=IntervalTrigger(minutes=settings.job_lock_cleanup_interval_minutes),
        id="cleanup_locks",
        replace_existing=True,
        kwargs={"bot": bot},
    )

    scheduler.add_job(
        cleanup_all_job,
        trigger=CronTrigger(hour=3, minute=0),
        id="cleanup_nightly",
        replace_existing=True,
        kwargs={"bot": bot},
    )

    scheduler.add_job(
        send_24h_reminders_job,
        trigger=IntervalTrigger(minutes=settings.job_reminder_interval_minutes),
        id="reminder_24h",
        replace_existing=True,
        kwargs={"bot": bot},
    )

    scheduler.add_job(
        send_2h_reminders_job,
        trigger=IntervalTrigger(minutes=settings.job_reminder_interval_minutes),
        id="reminder_2h",
        replace_existing=True,
        kwargs={"bot": bot},
    )

    scheduler.add_job(
        daily_report_job,
        trigger=CronTrigger(
            hour=settings.daily_report_hour,
            minute=settings.daily_report_minute,
        ),
        id="daily_report",
        replace_existing=True,
        kwargs={"bot": bot},
    )

    scheduler.add_job(
        generate_statistics_job,
        trigger=CronTrigger(
            hour=settings.daily_report_hour,
            minute=settings.daily_report_minute,
        ),
        id="generate_statistics",
        replace_existing=True,
        kwargs={"bot": bot},
    )

    logger.info(
        "Scheduler configured: report at %02d:%02d, reminders every %d min",
        settings.daily_report_hour,
        settings.daily_report_minute,
        settings.job_reminder_interval_minutes,
    )
    return scheduler
