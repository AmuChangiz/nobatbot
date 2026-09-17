from datetime import date, time

from app.bot.keyboards.markup import build_inline
from app.bot.bale_compat import CallbackQuery, F, FSMContext, Message, Router
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.admin import IsAdminFilter
from app.bot.filters.permissions import PermissionFilter
from app.bot.keyboards.admin import (
    inline_confirm_delete,
    inline_doctors_schedule,
    inline_schedule_detail,
    inline_schedules_admin,
)
from app.bot.permissions import Permission
from app.bot.states import AdminScheduleStates
from app.bot.texts import fa as t
from app.services import DoctorService, ScheduleService
from app.utils import format_date_persian, format_time, generate_slots, parse_date, parse_time

router = Router(name="admin_schedule")
router.message.filter(IsAdminFilter(), PermissionFilter(Permission.MANAGE_SCHEDULES))
router.callback_query.filter(IsAdminFilter(), PermissionFilter(Permission.MANAGE_SCHEDULES))


def _edit_fields_kb(schedule_id: int):
    return build_inline([
        [(t.BTN_EDIT_DATE, f"adm_sched_ef:date:{schedule_id}")],
        [(t.BTN_EDIT_START, f"adm_sched_ef:start:{schedule_id}")],
        [(t.BTN_EDIT_END, f"adm_sched_ef:end:{schedule_id}")],
        [(t.BTN_EDIT_DURATION, f"adm_sched_ef:dur:{schedule_id}")],
        [(t.BTN_BACK, f"adm_sched_view:{schedule_id}")],
    ])


@router.message(F.text == t.BTN_ADMIN_SCHEDULES)
async def schedule_pick_doctor(message: Message, session: AsyncSession) -> None:
    doctors = await DoctorService.list_all(session)
    active = [d for d in doctors if d.is_active]
    if not active:
        await message.answer("ابتدا یک پزشک فعال ایجاد کنید.")
        return
    await message.answer(t.SELECT_DOCTOR_FOR_SCHEDULE, reply_markup=inline_doctors_schedule(active))


@router.callback_query(F.data == "adm_sched_pick_doc")
async def schedule_pick_doc_back(callback: CallbackQuery, session: AsyncSession) -> None:
    doctors = await DoctorService.list_all(session)
    active = [d for d in doctors if d.is_active]
    await callback.message.edit_text(t.SELECT_DOCTOR_FOR_SCHEDULE, reply_markup=inline_doctors_schedule(active))
    await callback.answer()


@router.callback_query(F.data.startswith("adm_sched_doc:"))
async def list_schedules(callback: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    doctor_id = int(callback.data.split(":")[1])
    doctor = await DoctorService.get(session, doctor_id)
    if doctor is None:
        await callback.answer(t.ERROR_GENERIC, show_alert=True)
        return
    await state.update_data(schedule_doctor_id=doctor_id, schedule_doctor_name=doctor.name)
    schedules = await ScheduleService.list_by_doctor(session, doctor_id)
    await callback.message.edit_text(
        t.SCHEDULE_LIST_HEADER.format(doctor=doctor.name),
        reply_markup=inline_schedules_admin(schedules),
    )
    await callback.answer()


@router.callback_query(F.data == "adm_sched_back_list")
async def schedule_back_list(callback: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    data = await state.get_data()
    doctor_id = data.get("schedule_doctor_id")
    if not doctor_id:
        await callback.answer(t.ERROR_GENERIC, show_alert=True)
        return
    schedules = await ScheduleService.list_by_doctor(session, doctor_id)
    await callback.message.edit_text(
        t.SCHEDULE_LIST_HEADER.format(doctor=data.get("schedule_doctor_name", "")),
        reply_markup=inline_schedules_admin(schedules),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm_sched_view:"))
async def view_schedule(callback: CallbackQuery, session: AsyncSession) -> None:
    schedule_id = int(callback.data.split(":")[1])
    schedule = await ScheduleService.get(session, schedule_id)
    if schedule is None:
        await callback.answer(t.ERROR_GENERIC, show_alert=True)
        return
    slots = generate_slots(
        schedule.schedule_date, schedule.start_time, schedule.end_time, schedule.visit_duration_minutes
    )
    text = t.SCHEDULE_DETAIL.format(
        doctor=schedule.doctor.name,
        date=format_date_persian(schedule.schedule_date),
        start=format_time(schedule.start_time),
        end=format_time(schedule.end_time),
        duration=schedule.visit_duration_minutes,
        slot_count=len(slots),
    )
    await callback.message.edit_text(text, reply_markup=inline_schedule_detail(schedule_id))
    await callback.answer()


@router.callback_query(F.data == "adm_sched_add")
async def add_schedule_start(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    if "schedule_doctor_id" not in data:
        await callback.answer("ابتدا پزشک را انتخاب کنید.", show_alert=True)
        return
    await state.update_data(edit_schedule_id=None)
    await state.set_state(AdminScheduleStates.enter_date)
    await callback.message.edit_text(t.ENTER_SCHEDULE_DATE)
    await callback.answer()


@router.message(AdminScheduleStates.enter_date, F.text)
async def add_schedule_date(message: Message, state: FSMContext) -> None:
    schedule_date = parse_date(message.text)
    if schedule_date is None:
        await message.answer(t.INVALID_DATE)
        return
    await state.update_data(schedule_date=schedule_date.isoformat())
    await state.set_state(AdminScheduleStates.enter_start_time)
    await message.answer(t.ENTER_START_TIME)


@router.message(AdminScheduleStates.enter_start_time, F.text)
async def add_schedule_start_time(message: Message, state: FSMContext) -> None:
    start_time = parse_time(message.text)
    if start_time is None:
        await message.answer(t.INVALID_TIME)
        return
    await state.update_data(start_time=start_time.isoformat())
    await state.set_state(AdminScheduleStates.enter_end_time)
    await message.answer(t.ENTER_END_TIME)


@router.message(AdminScheduleStates.enter_end_time, F.text)
async def add_schedule_end_time(message: Message, state: FSMContext) -> None:
    end_time = parse_time(message.text)
    if end_time is None:
        await message.answer(t.INVALID_TIME)
        return
    data = await state.get_data()
    start_time = time.fromisoformat(data["start_time"])
    if end_time <= start_time:
        await message.answer(t.INVALID_TIME_RANGE)
        return
    await state.update_data(end_time=end_time.isoformat())
    await state.set_state(AdminScheduleStates.enter_duration)
    await message.answer(t.ENTER_VISIT_DURATION)


@router.message(AdminScheduleStates.enter_duration, F.text)
async def add_schedule_duration(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not message.text.strip().isdigit():
        await message.answer(t.INVALID_DURATION)
        return
    duration = int(message.text.strip())
    if duration <= 0:
        await message.answer(t.INVALID_DURATION)
        return

    data = await state.get_data()
    schedule_date = date.fromisoformat(data["schedule_date"])
    start_time = time.fromisoformat(data["start_time"])
    end_time = time.fromisoformat(data["end_time"])
    doctor_id = data["schedule_doctor_id"]
    slots = generate_slots(schedule_date, start_time, end_time, duration)
    if not slots:
        await message.answer(t.INVALID_TIME_RANGE)
        return

    try:
        await ScheduleService.create(session, doctor_id, schedule_date, start_time, end_time, duration)
    except IntegrityError:
        await session.rollback()
        await message.answer(t.SCHEDULE_EXISTS)
        return

    await state.set_state(None)
    await message.answer(
        t.SCHEDULE_CREATED.format(
            date=format_date_persian(schedule_date),
            start=format_time(start_time),
            end=format_time(end_time),
            duration=duration,
            slot_count=len(slots),
        ),
        reply_markup=inline_schedules_admin(await ScheduleService.list_by_doctor(session, doctor_id)),
    )


@router.callback_query(F.data.startswith("adm_sched_edit:"))
async def edit_schedule_menu(callback: CallbackQuery) -> None:
    schedule_id = int(callback.data.split(":")[1])
    await callback.message.edit_text(t.SELECT_SCHEDULE_FIELD, reply_markup=_edit_fields_kb(schedule_id))
    await callback.answer()


@router.callback_query(F.data.startswith("adm_sched_ef:"))
async def edit_schedule_field(callback: CallbackQuery, state: FSMContext) -> None:
    parts = callback.data.split(":")
    field, schedule_id = parts[2], int(parts[3])
    await state.update_data(edit_schedule_id=schedule_id, edit_field=field)
    prompts = {
        "date": (AdminScheduleStates.edit_date, t.ENTER_SCHEDULE_DATE),
        "start": (AdminScheduleStates.edit_start_time, t.ENTER_START_TIME),
        "end": (AdminScheduleStates.edit_end_time, t.ENTER_END_TIME),
        "dur": (AdminScheduleStates.edit_duration, t.ENTER_VISIT_DURATION),
    }
    st, prompt = prompts[field]
    await state.set_state(st)
    await callback.message.edit_text(prompt)
    await callback.answer()


async def _apply_schedule_edit(message: Message, state: FSMContext, session: AsyncSession, value) -> None:
    data = await state.get_data()
    schedule_id = data["edit_schedule_id"]
    field = data["edit_field"]
    kwargs = {}
    if field == "date":
        kwargs["schedule_date"] = value
    elif field == "start":
        kwargs["start_time"] = value
    elif field == "end":
        kwargs["end_time"] = value
    elif field == "dur":
        kwargs["visit_duration_minutes"] = value
    try:
        schedule = await ScheduleService.update(session, schedule_id, **kwargs)
    except IntegrityError:
        await session.rollback()
        await message.answer(t.SCHEDULE_EXISTS)
        return
    await state.clear()
    if schedule is None:
        await message.answer(t.ERROR_GENERIC)
        return
    slots = generate_slots(
        schedule.schedule_date, schedule.start_time, schedule.end_time, schedule.visit_duration_minutes
    )
    await message.answer(t.SCHEDULE_UPDATED)
    await message.answer(
        t.SCHEDULE_DETAIL.format(
            doctor=schedule.doctor.name,
            date=format_date_persian(schedule.schedule_date),
            start=format_time(schedule.start_time),
            end=format_time(schedule.end_time),
            duration=schedule.visit_duration_minutes,
            slot_count=len(slots),
        ),
        reply_markup=inline_schedule_detail(schedule_id),
    )


@router.message(AdminScheduleStates.edit_date, F.text)
async def edit_schedule_date(message: Message, state: FSMContext, session: AsyncSession) -> None:
    d = parse_date(message.text)
    if d is None:
        await message.answer(t.INVALID_DATE)
        return
    await _apply_schedule_edit(message, state, session, d)


@router.message(AdminScheduleStates.edit_start_time, F.text)
async def edit_schedule_start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    tm = parse_time(message.text)
    if tm is None:
        await message.answer(t.INVALID_TIME)
        return
    await _apply_schedule_edit(message, state, session, tm)


@router.message(AdminScheduleStates.edit_end_time, F.text)
async def edit_schedule_end(message: Message, state: FSMContext, session: AsyncSession) -> None:
    tm = parse_time(message.text)
    if tm is None:
        await message.answer(t.INVALID_TIME)
        return
    await _apply_schedule_edit(message, state, session, tm)


@router.message(AdminScheduleStates.edit_duration, F.text)
async def edit_schedule_duration(message: Message, state: FSMContext, session: AsyncSession) -> None:
    if not message.text.strip().isdigit():
        await message.answer(t.INVALID_DURATION)
        return
    duration = int(message.text.strip())
    if duration <= 0:
        await message.answer(t.INVALID_DURATION)
        return
    await _apply_schedule_edit(message, state, session, duration)


@router.callback_query(F.data.startswith("adm_sched_del:"))
async def delete_schedule_confirm(callback: CallbackQuery, session: AsyncSession) -> None:
    schedule_id = int(callback.data.split(":")[1])
    schedule = await ScheduleService.get(session, schedule_id)
    if schedule is None:
        await callback.answer(t.ERROR_GENERIC, show_alert=True)
        return
    label = format_date_persian(schedule.schedule_date)
    await callback.message.edit_text(
        t.CONFIRM_DELETE.format(name=label),
        reply_markup=inline_confirm_delete("sched", schedule_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm_del_yes:sched:"))
async def delete_schedule_yes(callback: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    schedule_id = int(callback.data.split(":")[2])
    data = await state.get_data()
    doctor_id = data.get("schedule_doctor_id")
    await ScheduleService.delete(session, schedule_id)
    await callback.message.edit_text(t.SCHEDULE_DELETED)
    if doctor_id:
        schedules = await ScheduleService.list_by_doctor(session, doctor_id)
        await callback.message.answer(
            t.SCHEDULE_LIST_HEADER.format(doctor=data.get("schedule_doctor_name", "")),
            reply_markup=inline_schedules_admin(schedules),
        )
    await callback.answer()
