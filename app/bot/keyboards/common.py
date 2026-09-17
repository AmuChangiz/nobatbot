from app.bot.keyboards.markup import build_inline, build_menu, menu_button
from app.bot.texts import fa as t


def main_menu_keyboard():
    return build_menu([
        [menu_button(t.BTN_NEW_APPOINTMENT)],
        [menu_button(t.BTN_MY_APPOINTMENTS)],
        [menu_button(t.BTN_ADDRESS), menu_button(t.BTN_SUPPORT)],
    ])


def cancel_keyboard():
    return build_menu([[menu_button(t.BTN_CANCEL)]])


def back_cancel_keyboard():
    return build_menu([
        [menu_button(t.BTN_BACK)],
        [menu_button(t.BTN_CANCEL)],
    ])


def confirm_keyboard():
    return build_menu([
        [menu_button(t.BTN_CONFIRM), menu_button(t.BTN_CANCEL)],
    ])


def inline_list(items: list[tuple[str, str]], columns: int = 1):
    rows: list[list[tuple[str, str]]] = []
    row: list[tuple[str, str]] = []
    for text, callback_data in items:
        row.append((text, callback_data))
        if len(row) >= columns:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    return build_inline(rows)


def inline_specialties(specialties: list):
    items = [(s.name, f"spec:{s.id}") for s in specialties]
    return inline_list(items)


def inline_doctors(doctors: list):
    items = [(d.name, f"doc:{d.id}") for d in doctors]
    return inline_list(items)


def inline_dates(dates: list, doctor_id: int):
    from app.utils import format_date_persian

    items = [(format_date_persian(d), f"date:{doctor_id}:{d.isoformat()}") for d in dates]
    return inline_list(items)


def inline_slots(slots: list):
    from app.utils import format_time

    items = [
        (format_time(s.slot_time), f"slot:{s.schedule_id}:{s.slot_time.strftime('%H:%M:%S')}")
        for s in slots
    ]
    return inline_list(items, columns=3)


def inline_appointments(appointments: list):
    from app.utils import format_date_persian, format_time

    items = []
    for appt in appointments:
        label = (
            f"{appt.doctor.name} — "
            f"{format_date_persian(appt.schedule.schedule_date)} "
            f"{format_time(appt.slot_time)}"
        )
        items.append((label, f"appt:{appt.id}"))
    return inline_list(items)


def inline_admin_specialties(specialties: list):
    items = []
    for s in specialties:
        status = "✅" if s.is_active else "❌"
        items.append((f"{status} {s.name}", f"adm_spec:{s.id}"))
    items.append((t.BTN_ADD_SPECIALTY, "adm_spec_add"))
    items.append((t.BTN_BACK, "adm_back"))
    return inline_list(items)


def inline_admin_doctors(doctors: list):
    items = []
    for d in doctors:
        status = "✅" if d.is_active else "❌"
        items.append((f"{status} {d.name}", f"adm_doc:{d.id}"))
    items.append((t.BTN_ADD_DOCTOR, "adm_doc_add"))
    items.append((t.BTN_BACK, "adm_back"))
    return inline_list(items)


def inline_admin_doctors_for_schedule(doctors: list):
    items = [(d.name, f"adm_sched_doc:{d.id}") for d in doctors if d.is_active]
    items.append((t.BTN_BACK, "adm_back"))
    return inline_list(items)


def inline_admin_schedules(schedules: list):
    from app.utils import format_date_persian, format_time

    items = []
    for s in schedules:
        label = (
            f"{format_date_persian(s.schedule_date)} "
            f"({format_time(s.start_time)}-{format_time(s.end_time)}, "
            f"{s.visit_duration_minutes}د)"
        )
        items.append((label, f"adm_sched:{s.id}"))
    items.append((t.BTN_ADD_SCHEDULE, "adm_sched_add"))
    items.append((t.BTN_BACK, "adm_back"))
    return inline_list(items)


def inline_admin_actions(entity: str, entity_id: int):
    return build_inline([
        [(t.BTN_TOGGLE_ACTIVE, f"adm_toggle:{entity}:{entity_id}")],
        [(t.BTN_BACK, f"adm_{entity}_list")],
    ])


def inline_confirm_cancel(appointment_id: int):
    return build_inline([
        [
            (t.BTN_CONFIRM, f"cancel_yes:{appointment_id}"),
            (t.BTN_CANCEL, "cancel_no"),
        ],
    ])


def inline_admin_list(admins: list):
    items = []
    for admin in admins:
        label = admin.display_name or str(admin.bale_user_id)
        if admin.is_superadmin:
            label = f"⭐ {label}"
        if not admin.is_superadmin:
            items.append((f"❌ {label}", f"adm_rm:{admin.id}"))
        else:
            items.append((label, f"adm_info:{admin.id}"))
    items.append((t.BTN_ADD_ADMIN, "adm_add"))
    items.append((t.BTN_BACK, "adm_back"))
    return inline_list(items)
