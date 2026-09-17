from app.bot.texts import fa as t

ADMIN_MENU_BUTTONS: frozenset[str] = frozenset(
    {
        t.BTN_ADMIN_SPECIALTIES,
        t.BTN_ADMIN_DOCTORS,
        t.BTN_ADMIN_SCHEDULES,
        t.BTN_ADMIN_APPOINTMENTS,
        t.BTN_ADMIN_ANNOUNCEMENTS,
        t.BTN_ADMIN_ADDRESS,
        t.BTN_ADMIN_SUPPORT,
        t.BTN_ADMIN_ADMINS,
        t.BTN_ADMIN_SETTINGS,
        t.BTN_ADMIN_STATS,
        t.BTN_ADMIN_BROADCAST,
        t.BTN_ADMIN_EXIT,
        t.BTN_CANCEL,
    }
)
