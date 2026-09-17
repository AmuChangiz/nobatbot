import logging

from app.bot.bale_compat import Bot

from app.bot.texts import fa as t
from app.db.session import get_session_factory
from app.scheduler.runner import scheduled_job
from app.services import AdminService, ReportService
from app.services.notifications import NotificationService
from app.services.statistics import StatisticsService
from app.utils import format_date_persian, format_time, today_local

logger = logging.getLogger(__name__)


@scheduled_job("گزارش روزانه")
async def daily_report_job(bot: Bot) -> None:
    session_factory = get_session_factory()
    report_date = today_local()

    async with session_factory() as session:
        report = await ReportService.daily_report(session, report_date)

        if report["today_appointments"]:
            lines = [
                t.REPORT_APPOINTMENT_LINE.format(
                    time=format_time(a.slot_time),
                    doctor=a.doctor.name,
                    patient=a.patient_name,
                )
                for a in report["today_appointments"]
            ]
            appointments_text = "\n".join(lines)
        else:
            appointments_text = t.NO_APPOINTMENTS_TODAY

        text = t.DAILY_REPORT.format(
            date=format_date_persian(report_date),
            new_users=report["new_users"],
            new_appointments=report["new_appointments"],
            cancelled=report["cancelled_appointments"],
            count=len(report["today_appointments"]),
            appointments=appointments_text,
        )

        admins = await AdminService.list_admins(session)
        for admin in admins:
            try:
                await bot.send_message(admin.bale_user_id, text)
            except Exception:
                logger.exception("Daily report failed for admin %d", admin.bale_user_id)
        await session.commit()

    logger.info("Daily report sent for %s", report_date)


@scheduled_job("تولید آمار")
async def generate_statistics_job(bot: Bot) -> None:
    session_factory = get_session_factory()
    stat_date = today_local()

    async with session_factory() as session:
        snapshot = await StatisticsService.generate_daily_snapshot(session, stat_date)
        await session.commit()

    detail = t.NOTIFY_STATS_GENERATED.format(
        date=format_date_persian(stat_date),
        new_users=snapshot.new_users,
        new_appointments=snapshot.new_appointments,
        confirmed=snapshot.confirmed_appointments,
    )
    await NotificationService.notify_job_summary(bot, "تولید آمار روزانه", detail)
    logger.info("Statistics snapshot saved for %s", stat_date)
