from datetime import date, time

from app.bot.bale_compat import Bot, CallbackQuery, F, FSMContext, Message, Router
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.helpers.booking_nav import (
    navigate_back,
    restore_booking_step,
    show_confirm_step,
    show_date_step,
    show_doctor_step,
    show_name_step,
    show_phone_step,
    show_specialty_step,
    show_time_step,
)
from app.bot.keyboards.common import main_menu_keyboard
from app.bot.keyboards.user import inline_resume_booking
from app.bot.states import BookingStates
from app.bot.texts import fa as t
from app.db.models import User
from app.services import (
    AppointmentService,
    DoctorService,
    SlotService,
    SpecialtyService,
)
from app.services.notifications import NotificationService
from app.utils import (
    format_date_persian,
    format_time,
    is_valid_phone,
    normalize_phone,
)

router = Router(name="booking")


@router.message(F.text == t.BTN_NEW_APPOINTMENT)
async def start_booking(message: Message, state: FSMContext, session: AsyncSession) -> None:
    current = await state.get_state()
    if current and current.startswith("BookingStates"):
        await message.answer(t.BOOKING_IN_PROGRESS, reply_markup=inline_resume_booking())
        return
    await state.clear()
    await show_specialty_step(message, session, state)


@router.callback_query(F.data == "book_resume")
async def resume_booking(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    db_user: User,
) -> None:
    await callback.message.edit_text(t.STATE_RECOVERED)
    await restore_booking_step(callback, session, state, db_user)
    await callback.answer()


@router.callback_query(F.data == "book_restart")
async def restart_booking(callback: CallbackQuery, state: FSMContext, session: AsyncSession, db_user: User) -> None:
    await SlotService.release_user_locks(session, db_user.id)
    await state.clear()
    await callback.message.delete()
    await show_specialty_step(callback.message, session, state)
    await callback.answer()


@router.callback_query(F.data == "book_cancel")
async def cancel_booking_callback(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    db_user: User,
) -> None:
    await SlotService.release_user_locks(session, db_user.id)
    await state.clear()
    await callback.message.edit_text(t.BOOKING_CANCELLED)
    await callback.message.answer(t.MAIN_MENU, reply_markup=main_menu_keyboard())
    await callback.answer()


@router.callback_query(F.data == "book_back")
async def booking_back_callback(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    db_user: User,
) -> None:
    await navigate_back(callback, session, state, db_user)
    await callback.answer()


@router.callback_query(BookingStates.select_specialty, F.data.startswith("book_spec:"))
async def select_specialty(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    specialty_id = int(callback.data.split(":")[1])
    doctors = await DoctorService.list_by_specialty(session, specialty_id)

    if not doctors:
        await callback.message.edit_text(t.NO_DOCTORS)
        await callback.answer()
        return

    slots_exist = False
    for doctor in doctors:
        available = await SlotService.get_available_slots_for_doctor(session, doctor.id)
        if available:
            slots_exist = True
            break

    if not slots_exist:
        await callback.message.edit_text(t.NO_AVAILABLE_APPOINTMENTS)
        await callback.answer()
        await state.clear()
        return

    await show_doctor_step(callback, session, state, specialty_id)
    await callback.answer()


@router.callback_query(BookingStates.select_doctor, F.data.startswith("book_doc:"))
async def select_doctor(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    doctor_id = int(callback.data.split(":")[1])
    doctor = await DoctorService.get(session, doctor_id)

    if doctor is None:
        await callback.answer(t.ERROR_GENERIC, show_alert=True)
        return

    await state.update_data(doctor_id=doctor_id, doctor_name=doctor.name)
    success = await show_date_step(callback, session, state, doctor_id)
    if not success:
        await state.clear()
    await callback.answer()


@router.callback_query(BookingStates.select_date, F.data.startswith("book_date:"))
async def select_date(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    parts = callback.data.split(":")
    doctor_id = int(parts[1])
    schedule_date = date.fromisoformat(parts[2])

    success = await show_time_step(callback, session, state, doctor_id, schedule_date)
    if not success:
        await callback.answer(t.NO_AVAILABLE_SLOTS, show_alert=True)
        return
    await callback.answer()


@router.callback_query(F.data.startswith("book_slot:"))
async def select_time(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    db_user: User,
) -> None:
    parts = callback.data.split(":")
    schedule_id = int(parts[1])
    slot_time = time.fromisoformat(parts[2])

    locked = await SlotService.lock_slot(session, db_user.id, schedule_id, slot_time)
    if not locked:
        data = await state.get_data()
        doctor_id = data.get("doctor_id")
        schedule_date_str = data.get("schedule_date")
        if doctor_id and schedule_date_str:
            from app.bot.keyboards.user import inline_slots_booking

            slots = await SlotService.get_available_slots_for_date(
                session, doctor_id, date.fromisoformat(schedule_date_str)
            )
            await callback.message.edit_text(
                f"{t.SLOT_TAKEN}\n\n{t.SELECT_TIME}",
                reply_markup=inline_slots_booking(slots),
            )
        else:
            await callback.message.edit_text(t.SLOT_TAKEN)
        await callback.answer()
        return

    await state.set_state(BookingStates.enter_phone)
    await state.update_data(schedule_id=schedule_id, slot_time=parts[2])
    await callback.message.delete()
    await show_phone_step(callback.message, state)
    await callback.answer()


@router.message(BookingStates.enter_phone, F.contact)
async def enter_phone_contact(message: Message, state: FSMContext) -> None:
    from app.bot.keyboards.user import phone_share_keyboard

    if message.contact is None or not message.contact.phone_number:
        await message.answer(t.INVALID_PHONE, reply_markup=phone_share_keyboard())
        return

    phone = normalize_phone(message.contact.phone_number)
    if not is_valid_phone(phone):
        await message.answer(t.INVALID_PHONE, reply_markup=phone_share_keyboard())
        return

    await state.update_data(patient_phone=phone)
    await show_name_step(message, state)


@router.message(BookingStates.enter_phone, F.text)
async def enter_phone_text(message: Message, state: FSMContext, session: AsyncSession, db_user: User) -> None:
    from app.bot.keyboards.user import phone_share_keyboard

    if message.text == t.BTN_CANCEL:
        await _cancel_booking(message, state, session, db_user)
        return
    if message.text == t.BTN_BACK:
        await navigate_back(message, session, state, db_user)
        return

    phone = normalize_phone(message.text)
    if not is_valid_phone(phone):
        await message.answer(t.INVALID_PHONE, reply_markup=phone_share_keyboard())
        return

    await state.update_data(patient_phone=phone)
    await show_name_step(message, state)


@router.message(BookingStates.enter_name, F.text)
async def enter_name(message: Message, state: FSMContext, session: AsyncSession, db_user: User) -> None:
    if message.text == t.BTN_CANCEL:
        await _cancel_booking(message, state, session, db_user)
        return
    if message.text == t.BTN_BACK:
        await navigate_back(message, session, state, db_user)
        return

    name = message.text.strip()
    if len(name) < 3:
        from app.bot.keyboards.user import name_input_keyboard

        await message.answer(t.INVALID_NAME, reply_markup=name_input_keyboard())
        return

    await state.update_data(patient_name=name)
    await show_confirm_step(message, state)


@router.message(BookingStates.confirm, F.text == t.BTN_CONFIRM)
async def confirm_booking(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    db_user: User,
    bot: Bot,
) -> None:
    data = await state.get_data()

    appointment = await AppointmentService.book(
        session,
        user_id=db_user.id,
        schedule_id=data["schedule_id"],
        slot_time=time.fromisoformat(data["slot_time"]),
        patient_name=data["patient_name"],
        patient_phone=data["patient_phone"],
        appointment_type=data.get("appointment_type", "in_person"),
    )

    await state.clear()

    if appointment is None:
        await message.answer(t.SLOT_TAKEN, reply_markup=main_menu_keyboard())
        return

    schedule_date = date.fromisoformat(data["schedule_date"])
    full_appt = await AppointmentService.get(session, appointment.id)
    if full_appt:
        await NotificationService.notify_booking_confirmed(bot, full_appt)

    await message.answer(
        t.BOOKING_SUCCESS.format(
            tracking_code=appointment.tracking_code,
            specialty=data.get("specialty_name", ""),
            doctor=data.get("doctor_name", ""),
            date=format_date_persian(schedule_date),
            time=format_time(time.fromisoformat(data["slot_time"])),
        ),
        reply_markup=main_menu_keyboard(),
    )


@router.message(BookingStates.confirm, F.text == t.BTN_BACK)
async def confirm_back(message: Message, state: FSMContext, session: AsyncSession, db_user: User) -> None:
    await navigate_back(message, session, state, db_user)


@router.message(BookingStates.confirm, F.text == t.BTN_CANCEL)
async def confirm_cancel(message: Message, state: FSMContext, session: AsyncSession, db_user: User) -> None:
    await _cancel_booking(message, state, session, db_user)


@router.message(F.text == t.BTN_CANCEL)
async def cancel_any_booking(message: Message, state: FSMContext, session: AsyncSession, db_user: User) -> None:
    current = await state.get_state()
    if current and current.startswith("BookingStates"):
        await _cancel_booking(message, state, session, db_user)


@router.message(F.text == t.BTN_BACK)
async def back_any_booking(message: Message, state: FSMContext, session: AsyncSession, db_user: User) -> None:
    current = await state.get_state()
    if current and current.startswith("BookingStates"):
        await navigate_back(message, session, state, db_user)


async def _cancel_booking(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    db_user: User,
) -> None:
    await SlotService.release_user_locks(session, db_user.id)
    await state.clear()
    await message.answer(t.BOOKING_CANCELLED, reply_markup=main_menu_keyboard())
