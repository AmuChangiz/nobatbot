from app.bot.keyboards.markup import build_inline, build_menu, menu_button
from app.bot.permissions import Permission, has_permission
from app.bot.texts import fa as t


def _inline(items: list[tuple[str, str]], back: str = "adm_back", columns: int = 1):
    rows: list[list[tuple[str, str]]] = []
    row: list[tuple[str, str]] = []
    for text, cb in items:
        row.append((text, cb))
        if len(row) >= columns:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([(t.BTN_BACK, back)])
    return build_inline(rows)


def admin_menu_keyboard(admin):
    rows: list[list] = []
    mapping = [
        (Permission.MANAGE_SPECIALTIES, t.BTN_ADMIN_SPECIALTIES),
        (Permission.MANAGE_DOCTORS, t.BTN_ADMIN_DOCTORS),
        (Permission.MANAGE_SCHEDULES, t.BTN_ADMIN_SCHEDULES),
        (Permission.MANAGE_APPOINTMENTS, t.BTN_ADMIN_APPOINTMENTS),
        (Permission.MANAGE_ANNOUNCEMENTS, t.BTN_ADMIN_ANNOUNCEMENTS),
        (Permission.MANAGE_ADDRESS, t.BTN_ADMIN_ADDRESS),
        (Permission.MANAGE_SUPPORT, t.BTN_ADMIN_SUPPORT),
        (Permission.MANAGE_ADMINS, t.BTN_ADMIN_ADMINS),
        (Permission.MANAGE_SETTINGS, t.BTN_ADMIN_SETTINGS),
        (Permission.VIEW_STATS, t.BTN_ADMIN_STATS),
        (Permission.BROADCAST, t.BTN_ADMIN_BROADCAST),
    ]
    for perm, label in mapping:
        if has_permission(admin, perm):
            rows.append([menu_button(label)])
    rows.append([menu_button(t.BTN_ADMIN_EXIT)])
    return build_menu(rows)


def admin_cancel_kb():
    return build_menu([[menu_button(t.BTN_CANCEL)]])


def inline_specialties_admin(specialties: list, back: str = "adm_back"):
    items = []
    for s in specialties:
        status = "✅" if s.is_active else "❌"
        items.append((f"{status} {s.name}", f"adm_spec:{s.id}"))
    items.append((t.BTN_ADD_SPECIALTY, "adm_spec_add"))
    return _inline(items, back=back)


def inline_specialty_detail(specialty_id: int):
    return build_inline([
        [(t.BTN_EDIT, f"adm_spec_edit:{specialty_id}")],
        [(t.BTN_TOGGLE_ACTIVE, f"adm_toggle:spec:{specialty_id}")],
        [(t.BTN_DELETE, f"adm_spec_del:{specialty_id}")],
        [(t.BTN_BACK, "adm_spec_list")],
    ])


def inline_doctors_admin(doctors: list):
    items = []
    for d in doctors:
        status = "✅" if d.is_active else "❌"
        items.append((f"{status} {d.name}", f"adm_doc:{d.id}"))
    items.append((t.BTN_ADD_DOCTOR, "adm_doc_add"))
    return _inline(items)


def inline_doctor_detail(doctor_id: int):
    return build_inline([
        [(t.BTN_EDIT, f"adm_doc_edit:{doctor_id}")],
        [(t.BTN_TOGGLE_ACTIVE, f"adm_toggle:doc:{doctor_id}")],
        [(t.BTN_DELETE, f"adm_doc_del:{doctor_id}")],
        [(t.BTN_BACK, "adm_doc_list")],
    ])


def inline_specialties_pick(specialties: list, prefix: str = "adm_pick_spec"):
    items = [(s.name, f"{prefix}:{s.id}") for s in specialties if s.is_active]
    return _inline(items, back="adm_doc_list")


def inline_doctors_schedule(doctors: list):
    items = [(d.name, f"adm_sched_doc:{d.id}") for d in doctors if d.is_active]
    return _inline(items)


def inline_schedules_admin(schedules: list):
    from app.utils import format_date_persian, format_time

    items = []
    for s in schedules:
        label = (
            f"{format_date_persian(s.schedule_date)} "
            f"({format_time(s.start_time)}-{format_time(s.end_time)}, {s.visit_duration_minutes}د)"
        )
        items.append((label, f"adm_sched_view:{s.id}"))
    items.append((t.BTN_ADD_SCHEDULE, "adm_sched_add"))
    return _inline(items, back="adm_sched_pick_doc")


def inline_schedule_detail(schedule_id: int):
    return build_inline([
        [(t.BTN_EDIT, f"adm_sched_edit:{schedule_id}")],
        [(t.BTN_DELETE, f"adm_sched_del:{schedule_id}")],
        [(t.BTN_BACK, "adm_sched_back_list")],
    ])


def inline_confirm_delete(entity: str, entity_id: int):
    return build_inline([
        [
            (t.BTN_CONFIRM, f"adm_del_yes:{entity}:{entity_id}"),
            (t.BTN_CANCEL, f"adm_del_no:{entity}:{entity_id}"),
        ],
    ])


def inline_appointments_admin_menu():
    return build_inline([
        [(t.BTN_SEARCH_APPOINTMENT, "adm_appt_search")],
        [(t.BTN_RECENT_APPOINTMENTS, "adm_appt_recent")],
        [(t.BTN_BACK, "adm_back")],
    ])


def inline_appointments_search_results(appointments: list):
    from app.utils import format_date_persian, format_time

    items = []
    for a in appointments:
        label = (
            f"🔖 {a.tracking_code} — {a.patient_name} — "
            f"{format_date_persian(a.schedule.schedule_date)} {format_time(a.slot_time)}"
        )
        items.append((label, f"adm_appt:{a.id}"))
    return _inline(items, back="adm_appt_menu")


def inline_appointment_admin_actions(appt_id: int):
    return build_inline([
        [(t.BTN_ADMIN_CANCEL_APPT, f"adm_appt_cancel:{appt_id}")],
        [(t.BTN_MARK_COMPLETED, f"adm_appt_complete:{appt_id}")],
        [(t.BTN_MARK_NO_SHOW, f"adm_appt_noshow:{appt_id}")],
        [(t.BTN_BACK, "adm_appt_menu")],
    ])


def inline_announcements_admin(items: list):
    rows = []
    for item in items:
        status = "✅" if item.is_active else "❌"
        rows.append((f"{status} {item.title}", f"adm_ann:{item.id}"))
    rows.append((t.BTN_ADD_ANNOUNCEMENT, "adm_ann_add"))
    return _inline(rows)


def inline_announcement_detail(ann_id: int):
    return build_inline([
        [(t.BTN_EDIT, f"adm_ann_edit:{ann_id}")],
        [(t.BTN_TOGGLE_ACTIVE, f"adm_ann_toggle:{ann_id}")],
        [(t.BTN_DELETE, f"adm_ann_del:{ann_id}")],
        [(t.BTN_BACK, "adm_ann_list")],
    ])


def inline_admins_list(admins: list, is_superadmin: bool):
    items = []
    for admin in admins:
        label = admin.display_name or str(admin.bale_user_id)
        label = f"⭐ {label}" if admin.is_superadmin else f"👤 {label}"
        items.append((label, f"adm_user:{admin.id}"))
    if is_superadmin:
        items.append((t.BTN_ADD_ADMIN, "adm_add"))
    return _inline(items)


def inline_admin_detail(admin_id: int, is_superadmin_viewer: bool, target_is_super: bool):
    rows: list[list[tuple[str, str]]] = []
    if is_superadmin_viewer and not target_is_super:
        rows.append([(t.BTN_PROMOTE_SUPER, f"adm_promote:{admin_id}")])
    if is_superadmin_viewer and target_is_super and admin_id:
        rows.append([(t.BTN_DEMOTE_ADMIN, f"adm_demote:{admin_id}")])
    if is_superadmin_viewer and not target_is_super:
        rows.append([(t.BTN_DELETE, f"adm_user_del:{admin_id}")])
    rows.append([(t.BTN_BACK, "adm_user_list")])
    return build_inline(rows)


def inline_settings_menu():
    return build_inline([
        [(t.BTN_VIEW_SETTINGS, "adm_set_view")],
        [(t.BTN_BACK, "adm_back")],
    ])
