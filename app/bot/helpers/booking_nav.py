from datetime import date, time

from app.bot.bale_compat import CallbackQuery, FSMContext, Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.common import main_menu_keyboard
from app.bot.keyboards.user import (
    confirm_booking_keyboard,
    inline_dates_booking,
    inline_doctors_booking,
    inline_slots_booking,
    inline_specialties_booking,
    name_input_keyboard,
    phone_share_keyboard,
)
from app.bot.states import BookingStates
from app.bot.texts import fa as t
from app.db.models import User
from app.services import DoctorService, SlotService, SpecialtyService
from app.utils import format_date_persian, format_time


async def push_step(state: FSMContext, step: str) -> None:
    data = await state.get_data()
    history: list[str] = data.get("step_history", [])
    if history and history[-1] == step:
        return
    history.append(step)
    await state.update_data(step_history=history)


async def pop_step(state: FSMContext) -> str | None:
    data = await state.get_data()
    history: list[str] = data.get("step_history", [])
    if len(history) < 2:
        return None
    history.pop()
    previous = history[-1]
    await state.update_data(step_history=history)
    return previous


async def show_specialty_step(
    target: Message | CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    *,
    push: bool = True,
) -> None:
    specialties = await SpecialtyService.list_active(session)
    if not specialties:
        text = t.NO_SPECIALTIES
        if isinstance(target, CallbackQuery):
            await target.message.edit_text(text)
            await target.message.answer(t.MAIN_MENU, reply_markup=main_menu_keyboard())
        else:
            await target.answer(text, reply_markup=main_menu_keyboard())
        await state.clear()
        return

    await state.set_state(BookingStates.select_specialty)
    if push:
        await state.update_data(step_history=["specialty"])
    text = t.SELECT_SPECIALTY
    kb = inline_specialties_booking(specialties)

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=kb)
    else:
        await target.answer(text, reply_markup=kb)


async def show_doctor_step(
    target: Message | CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    specialty_id: int,
    *,
    push: bool = True,
) -> bool:
    doctors = await DoctorService.list_by_specialty(session, specialty_id)
    if not doctors:
        text = t.NO_DOCTORS
        if isinstance(target, CallbackQuery):
            await target.message.edit_text(text)
        else:
            await target.answer(text)
        return False

    specialty = await SpecialtyService.get(session, specialty_id)
    await state.update_data(
        specialty_id=specialty_id,
        specialty_name=specialty.name if specialty else "",
    )
    await state.set_state(BookingStates.select_doctor)
    if push:
        await push_step(state, "doctor")

    kb = inline_doctors_booking(doctors)
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(t.SELECT_DOCTOR, reply_markup=kb)
    else:
        await target.answer(t.SELECT_DOCTOR, reply_markup=kb)
    return True


async def show_date_step(
    target: Message | CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    doctor_id: int,
    *,
    push: bool = True,
) -> bool:
    dates = await SlotService.get_available_dates_for_doctor(session, doctor_id)
    if not dates:
        text = t.NO_AVAILABLE_DATES
        if isinstance(target, CallbackQuery):
            await target.message.edit_text(text)
        else:
            await target.answer(text)
        return False

    await state.set_state(BookingStates.select_date)
    if push:
        await push_step(state, "date")
    kb = inline_dates_booking(dates, doctor_id)
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(t.SELECT_DATE, reply_markup=kb)
    else:
        await target.answer(t.SELECT_DATE, reply_markup=kb)
    return True


async def show_time_step(
    target: Message | CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    doctor_id: int,
    schedule_date: date,
    *,
    push: bool = True,
) -> bool:
    slots = await SlotService.get_available_slots_for_date(session, doctor_id, schedule_date)
    if not slots:
        text = t.NO_AVAILABLE_SLOTS
        if isinstance(target, CallbackQuery):
            await target.message.edit_text(text)
        else:
            await target.answer(text)
        return False

    await state.update_data(schedule_date=schedule_date.isoformat())
    await state.set_state(BookingStates.select_time)
    if push:
        await push_step(state, "time")
    kb = inline_slots_booking(slots)
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(t.SELECT_TIME, reply_markup=kb)
    else:
        await target.answer(t.SELECT_TIME, reply_markup=kb)
    return True


async def show_phone_step(message: Message, state: FSMContext, *, push: bool = True) -> None:
    await state.set_state(BookingStates.enter_phone)
    if push:
        await push_step(state, "phone")
    await message.answer(t.ENTER_PHONE, reply_markup=phone_share_keyboard())


async def show_name_step(message: Message, state: FSMContext, *, push: bool = True) -> None:
    await state.set_state(BookingStates.enter_name)
    if push:
        await push_step(state, "name")
    await message.answer(t.ENTER_NAME, reply_markup=name_input_keyboard())


async def show_confirm_step(message: Message, state: FSMContext, *, push: bool = True) -> None:
    data = await state.get_data()
    schedule_date = date.fromisoformat(data["schedule_date"])
    slot_time = time.fromisoformat(data["slot_time"])

    text = t.CONFIRM_BOOKING.format(
        tracking_preview="پس از تأیید صادر می‌شود",
        specialty=data.get("specialty_name", ""),
        doctor=data.get("doctor_name", ""),
        date=format_date_persian(schedule_date),
        time=format_time(slot_time),
        name=data.get("patient_name", ""),
        phone=data.get("patient_phone", ""),
    )
    await state.set_state(BookingStates.confirm)
    if push:
        await push_step(state, "confirm")
    await message.answer(text, reply_markup=confirm_booking_keyboard())


async def restore_booking_step(
    target: Message | CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    db_user: User,
) -> None:
    data = await state.get_data()
    current_state = await state.get_state()

    if not current_state or not current_state.startswith("BookingStates"):
        await show_specialty_step(target, session, state)
        return

    post_time_states = {
        BookingStates.enter_phone.state,
        BookingStates.enter_name.state,
        BookingStates.confirm.state,
    }
    if current_state in post_time_states:
        schedule_id = data.get("schedule_id")
        slot_time_str = data.get("slot_time")
        if schedule_id and slot_time_str:
            slot_time = time.fromisoformat(slot_time_str)
            locked = await SlotService.lock_slot(session, db_user.id, schedule_id, slot_time)
            if not locked:
                doctor_id = data.get("doctor_id")
                if isinstance(target, CallbackQuery):
                    await target.message.edit_text(t.LOCK_EXPIRED)
                    msg = target.message
                else:
                    await target.answer(t.LOCK_EXPIRED)
                    msg = target
                if doctor_id:
                    await show_time_step(
                        msg,
                        session,
                        state,
                        doctor_id,
                        date.fromisoformat(data["schedule_date"]),
                        push=False,
                    )
                return

    if current_state == BookingStates.select_specialty.state:
        await show_specialty_step(target, session, state, push=False)
    elif current_state == BookingStates.select_doctor.state:
        specialty_id = data.get("specialty_id")
        if specialty_id:
            await show_doctor_step(target, session, state, specialty_id, push=False)
        else:
            await show_specialty_step(target, session, state)
    elif current_state == BookingStates.select_appointment_type.state:
        doctor_id = data.get("doctor_id")
        if doctor_id:
            await show_date_step(target, session, state, doctor_id, push=False)
        else:
            await show_specialty_step(target, session, state)
    elif current_state == BookingStates.select_date.state:
        doctor_id = data.get("doctor_id")
        if doctor_id:
            await show_date_step(target, session, state, doctor_id, push=False)
        else:
            await show_specialty_step(target, session, state)
    elif current_state == BookingStates.select_time.state:
        doctor_id = data.get("doctor_id")
        schedule_date_str = data.get("schedule_date")
        if doctor_id and schedule_date_str:
            await show_time_step(
                target, session, state, doctor_id, date.fromisoformat(schedule_date_str), push=False
            )
        else:
            await show_specialty_step(target, session, state)
    elif current_state == BookingStates.enter_phone.state:
        if isinstance(target, CallbackQuery):
            await target.message.delete()
            await show_phone_step(target.message, state, push=False)
        else:
            await show_phone_step(target, state, push=False)
    elif current_state == BookingStates.enter_name.state:
        if isinstance(target, CallbackQuery):
            await target.message.delete()
            await show_name_step(target.message, state, push=False)
        else:
            await show_name_step(target, state, push=False)
    elif current_state == BookingStates.confirm.state:
        if isinstance(target, CallbackQuery):
            await target.message.delete()
            await show_confirm_step(target.message, state, push=False)
        else:
            await show_confirm_step(target, state, push=False)
    else:
        await show_specialty_step(target, session, state)


async def navigate_back(
    target: Message | CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    db_user: User,
) -> None:
    data = await state.get_data()
    history: list[str] = data.get("step_history", [])

    if len(history) <= 1:
        await SlotService.release_user_locks(session, db_user.id)
        await state.clear()
        if isinstance(target, Message):
            await target.answer(t.OPERATION_CANCELLED, reply_markup=main_menu_keyboard())
        else:
            await target.message.edit_text(t.OPERATION_CANCELLED)
            await target.message.answer(t.MAIN_MENU, reply_markup=main_menu_keyboard())
        return

    history.pop()
    previous = history[-1]
    await state.update_data(step_history=history)

    if previous == "specialty":
        await SlotService.release_user_locks(session, db_user.id)
        await show_specialty_step(target, session, state, push=False)
    elif previous == "doctor":
        await SlotService.release_user_locks(session, db_user.id)
        specialty_id = data.get("specialty_id")
        if specialty_id:
            await show_doctor_step(target, session, state, specialty_id, push=False)
    elif previous == "date":
        doctor_id = data.get("doctor_id")
        if doctor_id:
            await show_date_step(target, session, state, doctor_id, push=False)
    elif previous == "time":
        await SlotService.release_user_locks(session, db_user.id)
        doctor_id = data.get("doctor_id")
        if doctor_id:
            await show_date_step(target, session, state, doctor_id, push=False)
    elif previous == "phone":
        await SlotService.release_user_locks(session, db_user.id)
        doctor_id = data.get("doctor_id")
        schedule_date_str = data.get("schedule_date")
        if isinstance(target, CallbackQuery):
            await target.message.delete()
            msg = target.message
        else:
            msg = target
        if doctor_id and schedule_date_str:
            await show_time_step(
                msg, session, state, doctor_id, date.fromisoformat(schedule_date_str), push=False
            )
    elif previous == "name":
        if isinstance(target, CallbackQuery):
            await target.message.delete()
            await show_phone_step(target.message, state, push=False)
        else:
            await show_phone_step(target, state, push=False)
    elif previous == "confirm":
        if isinstance(target, CallbackQuery):
            await target.message.delete()
            await show_name_step(target.message, state, push=False)
        else:
            await show_name_step(target, state, push=False)
