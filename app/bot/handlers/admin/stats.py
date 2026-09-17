from app.bot.keyboards.markup import build_inline
from app.bot.bale_compat import CallbackQuery, F, FSMContext, Message, Router
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.admin import IsAdminFilter
from app.bot.filters.permissions import PermissionFilter
from app.bot.permissions import Permission
from app.bot.texts import fa as t
from app.services import ReportService, StatsService
from app.utils import format_date_persian, format_time, today_local

router = Router(name="admin_stats")
router.message.filter(IsAdminFilter(), PermissionFilter(Permission.VIEW_STATS))
router.callback_query.filter(IsAdminFilter(), PermissionFilter(Permission.VIEW_STATS))


def _stats_kb():
    return build_inline([
        [("📊 گزارش روزانه", "adm_stats_daily")],
        [(t.BTN_BACK, "adm_back")],
    ])


@router.message(F.text == t.BTN_ADMIN_STATS)
async def show_stats(message: Message, session: AsyncSession) -> None:
    stats = await StatsService.system_stats(session)
    text = t.SYSTEM_STATS.format(
        total_users=stats["total_users"],
        total_admins=stats["total_admins"],
        total_specialties=stats["total_specialties"],
        total_doctors=stats["total_doctors"],
        total_schedules=stats["total_schedules"],
        total_appointments=stats["total_appointments"],
        confirmed=stats["confirmed_appointments"],
        cancelled=stats["cancelled_appointments"],
        completed=stats["completed_appointments"],
        announcements=stats["active_announcements"],
        today=stats["today_appointments"],
    )
    await message.answer(text, reply_markup=_stats_kb())


@router.callback_query(F.data == "adm_stats_daily")
async def daily_report(callback: CallbackQuery, session: AsyncSession) -> None:
    report_date = today_local()
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
    await callback.message.edit_text(text, reply_markup=_stats_kb())
    await callback.answer()
