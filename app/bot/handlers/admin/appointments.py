from app.bot.bale_compat import Bot, CallbackQuery, F, FSMContext, Message, Router
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.admin import IsAdminFilter
from app.bot.filters.permissions import PermissionFilter
from app.bot.keyboards.admin import (
    inline_appointment_admin_actions,
    inline_appointments_admin_menu,
    inline_appointments_search_results,
)
from app.bot.permissions import Permission
from app.bot.states import AdminAppointmentStates
from app.bot.texts import fa as t
from app.db.models import AppointmentStatus
from app.services import AppointmentService
from app.services.notifications import NotificationService
from app.utils import format_date_persian, format_time

router = Router(name="admin_appointments")
router.message.filter(IsAdminFilter(), PermissionFilter(Permission.MANAGE_APPOINTMENTS))
router.callback_query.filter(IsAdminFilter(), PermissionFilter(Permission.MANAGE_APPOINTMENTS))

STATUS_LABELS = {
    AppointmentStatus.CONFIRMED: t.STATUS_CONFIRMED,
    AppointmentStatus.CANCELLED: t.STATUS_CANCELLED,
    AppointmentStatus.COMPLETED: t.STATUS_COMPLETED,
    AppointmentStatus.NO_SHOW: t.STATUS_NO_SHOW,
}


def _format_appt(appt) -> str:
    return t.APPOINTMENT_ADMIN_DETAIL.format(
        tracking_code=appt.tracking_code,
        name=appt.patient_name,
        phone=appt.patient_phone,
        doctor=appt.doctor.name,
        specialty=appt.doctor.specialty.name,
        date=format_date_persian(appt.schedule.schedule_date),
        time=format_time(appt.slot_time),
        status=STATUS_LABELS.get(appt.status, str(appt.status)),
    )


@router.message(F.text == t.BTN_ADMIN_APPOINTMENTS)
async def appointments_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(t.APPOINTMENTS_ADMIN_MENU, reply_markup=inline_appointments_admin_menu())


@router.callback_query(F.data == "adm_appt_menu")
async def cb_appt_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(t.APPOINTMENTS_ADMIN_MENU, reply_markup=inline_appointments_admin_menu())
    await callback.answer()


@router.callback_query(F.data == "adm_appt_search")
async def search_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminAppointmentStates.search_query)
    await callback.message.edit_text(t.ENTER_SEARCH_QUERY)
    await callback.answer()


@router.message(AdminAppointmentStates.search_query, F.text)
async def search_query(message: Message, state: FSMContext, session: AsyncSession) -> None:
    results = await AppointmentService.search(session, message.text.strip())
    await state.clear()
    if not results:
        await message.answer(t.SEARCH_NO_RESULTS, reply_markup=inline_appointments_admin_menu())
        return
    await message.answer(
        f"🔍 {len(results)} نتیجه یافت شد:",
        reply_markup=inline_appointments_search_results(results),
    )


@router.callback_query(F.data == "adm_appt_recent")
async def recent_appointments(callback: CallbackQuery, session: AsyncSession) -> None:
    results = await AppointmentService.list_recent(session)
    if not results:
        await callback.message.edit_text(t.SEARCH_NO_RESULTS, reply_markup=inline_appointments_admin_menu())
    else:
        await callback.message.edit_text(
            "🕐 آخرین رزروها:",
            reply_markup=inline_appointments_search_results(results),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("adm_appt:"))
async def view_appointment(callback: CallbackQuery, session: AsyncSession) -> None:
    appt_id = int(callback.data.split(":")[1])
    appt = await AppointmentService.get(session, appt_id)
    if appt is None:
        await callback.answer(t.ERROR_GENERIC, show_alert=True)
        return
    await callback.message.edit_text(_format_appt(appt), reply_markup=inline_appointment_admin_actions(appt_id))
    await callback.answer()


@router.callback_query(F.data.startswith("adm_appt_cancel:"))
async def admin_cancel(callback: CallbackQuery, session: AsyncSession, bot: Bot) -> None:
    appt_id = int(callback.data.split(":")[1])
    appt_before = await AppointmentService.get(session, appt_id)
    ok = await AppointmentService.admin_cancel(session, appt_id)
    await callback.answer(t.APPOINTMENT_STATUS_UPDATED if ok else t.ERROR_GENERIC, show_alert=not ok)
    if ok and appt_before:
        await NotificationService.notify_cancellation(bot, appt_before)
        appt = await AppointmentService.get(session, appt_id)
        await callback.message.edit_text(_format_appt(appt), reply_markup=inline_appointment_admin_actions(appt_id))


@router.callback_query(F.data.startswith("adm_appt_complete:"))
async def admin_complete(callback: CallbackQuery, session: AsyncSession) -> None:
    appt_id = int(callback.data.split(":")[1])
    ok = await AppointmentService.admin_set_status(session, appt_id, AppointmentStatus.COMPLETED)
    await callback.answer(t.APPOINTMENT_STATUS_UPDATED if ok else t.ERROR_GENERIC, show_alert=not ok)
    if ok:
        appt = await AppointmentService.get(session, appt_id)
        await callback.message.edit_text(_format_appt(appt), reply_markup=inline_appointment_admin_actions(appt_id))


@router.callback_query(F.data.startswith("adm_appt_noshow:"))
async def admin_noshow(callback: CallbackQuery, session: AsyncSession) -> None:
    appt_id = int(callback.data.split(":")[1])
    ok = await AppointmentService.admin_set_status(session, appt_id, AppointmentStatus.NO_SHOW)
    await callback.answer(t.APPOINTMENT_STATUS_UPDATED if ok else t.ERROR_GENERIC, show_alert=not ok)
    if ok:
        appt = await AppointmentService.get(session, appt_id)
        await callback.message.edit_text(_format_appt(appt), reply_markup=inline_appointment_admin_actions(appt_id))
