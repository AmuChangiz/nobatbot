from app.bot.bale_compat import Bot, CallbackQuery, F, FSMContext, Message, Router
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.common import main_menu_keyboard
from app.bot.keyboards.user import (
    inline_appointment_actions,
    inline_appointments_list,
    inline_confirm_cancel_appointment,
)
from app.bot.states import CancelAppointmentStates
from app.bot.texts import fa as t
from app.db.models import User
from app.services import AppointmentService
from app.services.notifications import NotificationService
from app.utils import format_date_persian, format_time

router = Router(name="appointments")


@router.message(F.text == t.BTN_MY_APPOINTMENTS)
async def list_appointments(message: Message, state: FSMContext, session: AsyncSession, db_user: User) -> None:
    await state.clear()
    appointments = await AppointmentService.get_user_appointments(session, db_user.id)
    if not appointments:
        await message.answer(t.MY_APPOINTMENTS_EMPTY, reply_markup=main_menu_keyboard())
        return

    lines = [t.MY_APPOINTMENTS_HEADER, ""]
    for appt in appointments:
        lines.append(
            t.APPOINTMENT_ITEM.format(
                tracking_code=appt.tracking_code,
                doctor=appt.doctor.name,
                specialty=appt.doctor.specialty.name,
                date=format_date_persian(appt.schedule.schedule_date),
                time=format_time(appt.slot_time),
                status=t.STATUS_CONFIRMED,
            )
        )
        lines.append("")

    await message.answer(
        "\n".join(lines),
        reply_markup=inline_appointments_list(appointments),
    )


@router.callback_query(F.data == "appt_back_menu")
async def appointments_back_menu(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(t.MAIN_MENU)
    await callback.message.answer(t.MAIN_MENU, reply_markup=main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "appt_back_list")
async def appointments_back_list(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    db_user: User,
) -> None:
    await state.clear()
    appointments = await AppointmentService.get_user_appointments(session, db_user.id)
    if not appointments:
        await callback.message.edit_text(t.MY_APPOINTMENTS_EMPTY)
        await callback.message.answer(t.MAIN_MENU, reply_markup=main_menu_keyboard())
        await callback.answer()
        return

    lines = [t.MY_APPOINTMENTS_HEADER, ""]
    for appt in appointments:
        lines.append(
            t.APPOINTMENT_ITEM.format(
                tracking_code=appt.tracking_code,
                doctor=appt.doctor.name,
                specialty=appt.doctor.specialty.name,
                date=format_date_persian(appt.schedule.schedule_date),
                time=format_time(appt.slot_time),
                status=t.STATUS_CONFIRMED,
            )
        )
        lines.append("")

    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=inline_appointments_list(appointments),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("appt_view:"))
async def view_appointment(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    db_user: User,
) -> None:
    appointment_id = int(callback.data.split(":")[1])
    appointment = await AppointmentService.get(session, appointment_id)
    if appointment is None or appointment.user_id != db_user.id:
        await callback.answer(t.ERROR_GENERIC, show_alert=True)
        return

    text = t.APPOINTMENT_DETAILS.format(
        tracking_code=appointment.tracking_code,
        doctor=appointment.doctor.name,
        specialty=appointment.doctor.specialty.name,
        date=format_date_persian(appointment.schedule.schedule_date),
        time=format_time(appointment.slot_time),
        name=appointment.patient_name,
        phone=appointment.patient_phone,
        status=t.STATUS_CONFIRMED,
    )

    await state.set_state(CancelAppointmentStates.select_appointment)
    await state.update_data(appointment_id=appointment_id)
    await callback.message.edit_text(text, reply_markup=inline_appointment_actions(appointment_id))
    await callback.answer()


@router.callback_query(F.data.startswith("appt_cancel:"))
async def request_cancel_appointment(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    db_user: User,
) -> None:
    appointment_id = int(callback.data.split(":")[1])
    appointment = await AppointmentService.get(session, appointment_id)
    if appointment is None or appointment.user_id != db_user.id:
        await callback.answer(t.ERROR_GENERIC, show_alert=True)
        return

    details = t.APPOINTMENT_ITEM.format(
        tracking_code=appointment.tracking_code,
        doctor=appointment.doctor.name,
        specialty=appointment.doctor.specialty.name,
        date=format_date_persian(appointment.schedule.schedule_date),
        time=format_time(appointment.slot_time),
        status=t.STATUS_CONFIRMED,
    )

    await state.set_state(CancelAppointmentStates.confirm)
    await state.update_data(appointment_id=appointment_id)
    await callback.message.edit_text(
        t.CONFIRM_CANCEL.format(details=details),
        reply_markup=inline_confirm_cancel_appointment(appointment_id),
    )
    await callback.answer()


@router.callback_query(CancelAppointmentStates.confirm, F.data.startswith("appt_cancel_yes:"))
async def confirm_cancel(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    db_user: User,
    bot: Bot,
) -> None:
    appointment_id = int(callback.data.split(":")[1])
    appt_before = await AppointmentService.get(session, appointment_id)
    success = await AppointmentService.cancel(session, appointment_id, db_user.id)
    await state.clear()

    if success:
        if appt_before:
            await NotificationService.notify_cancellation(bot, appt_before)
        await callback.message.edit_text(t.CANCEL_SUCCESS)
        await callback.message.answer(t.MAIN_MENU, reply_markup=main_menu_keyboard())
    else:
        await callback.message.edit_text(t.CANCEL_FAILED)
    await callback.answer()
