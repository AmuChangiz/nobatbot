from bale import InlineKeyboardButton

from app.bot.keyboards.common import main_menu_keyboard
from app.bot.keyboards.markup import build_inline, build_menu, menu_button
from app.bot.texts import fa as t


def inline_list_with_back(
    items: list[tuple[str, str]],
    back_callback: str = "book_back",
    columns: int = 1,
):
    rows: list[list[tuple[str, str]]] = []
    row: list[tuple[str, str]] = []
    for text, callback_data in items:
        row.append((text, callback_data))
        if len(row) >= columns:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([(t.BTN_BACK, back_callback)])
    return build_inline(rows)


def inline_specialties_booking(specialties: list):
    items = [(s.name, f"book_spec:{s.id}") for s in specialties]
    return inline_list_with_back(items, back_callback="book_cancel")


def inline_doctors_booking(doctors: list):
    items = [(d.name, f"book_doc:{d.id}") for d in doctors]
    return inline_list_with_back(items)


def inline_dates_booking(dates: list, doctor_id: int):
    from app.utils import format_date_persian

    items = [(format_date_persian(d), f"book_date:{doctor_id}:{d.isoformat()}") for d in dates]
    return inline_list_with_back(items)


def inline_slots_booking(slots: list):
    from app.utils import format_time

    items = [
        (format_time(s.slot_time), f"book_slot:{s.schedule_id}:{s.slot_time.strftime('%H:%M:%S')}")
        for s in slots
    ]
    return inline_list_with_back(items, columns=3)


def inline_resume_booking():
    return build_inline([
        [(t.BTN_RESUME_BOOKING, "book_resume")],
        [(t.BTN_NEW_BOOKING, "book_restart")],
        [(t.BTN_CANCEL, "book_cancel")],
    ])


def inline_appointments_list(appointments: list):
    from app.utils import format_date_persian, format_time

    items = []
    for appt in appointments:
        label = (
            f"🔖 {appt.tracking_code} — {appt.doctor.name} — "
            f"{format_date_persian(appt.schedule.schedule_date)} {format_time(appt.slot_time)}"
        )
        items.append((label, f"appt_view:{appt.id}"))
    return inline_list_with_back(items, back_callback="appt_back_menu", columns=1)


def inline_appointment_actions(appointment_id: int):
    return build_inline([
        [(t.BTN_CANCEL_APPOINTMENT, f"appt_cancel:{appointment_id}")],
        [(t.BTN_BACK, "appt_back_list")],
    ])


def inline_confirm_cancel_appointment(appointment_id: int):
    return build_inline([
        [
            (t.BTN_CONFIRM, f"appt_cancel_yes:{appointment_id}"),
            (t.BTN_BACK, f"appt_view:{appointment_id}"),
        ],
    ])


def phone_share_keyboard():
    return build_menu([
        [menu_button(t.BTN_SHARE_PHONE, request_contact=True)],
        [menu_button(t.BTN_BACK)],
        [menu_button(t.BTN_CANCEL)],
    ])


def name_input_keyboard():
    return build_menu([
        [menu_button(t.BTN_BACK)],
        [menu_button(t.BTN_CANCEL)],
    ])


def confirm_booking_keyboard():
    return build_menu([
        [menu_button(t.BTN_CONFIRM), menu_button(t.BTN_BACK)],
        [menu_button(t.BTN_CANCEL)],
    ])
