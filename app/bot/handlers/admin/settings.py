from app.bot.bale_compat import CallbackQuery, F, Message, Router

from app.bot.filters.admin import IsAdminFilter
from app.bot.filters.permissions import PermissionFilter
from app.bot.keyboards.admin import inline_settings_menu
from app.bot.permissions import Permission
from app.bot.texts import fa as t
from app.config import get_settings

router = Router(name="admin_settings")
router.message.filter(IsAdminFilter(), PermissionFilter(Permission.MANAGE_SETTINGS))
router.callback_query.filter(IsAdminFilter(), PermissionFilter(Permission.MANAGE_SETTINGS))


def _settings_text() -> str:
    settings = get_settings()
    return t.SETTINGS_HEADER.format(
        timezone=settings.timezone,
        slot_lock=settings.slot_lock_ttl_seconds,
        reminder_24h=settings.reminder_24h_hours,
        reminder_2h=settings.reminder_2h_hours,
        report_hour=settings.daily_report_hour,
        report_minute=settings.daily_report_minute,
        reminder_interval=settings.job_reminder_interval_minutes,
    )


@router.message(F.text == t.BTN_ADMIN_SETTINGS)
async def show_settings(message: Message) -> None:
    await message.answer(_settings_text(), reply_markup=inline_settings_menu())


@router.callback_query(F.data == "adm_set_view")
async def cb_settings(callback: CallbackQuery) -> None:
    await callback.message.edit_text(_settings_text(), reply_markup=inline_settings_menu())
    await callback.answer()
