import enum


class AdminRole(str, enum.Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"


class Permission(str, enum.Enum):
    MANAGE_SPECIALTIES = "manage_specialties"
    MANAGE_DOCTORS = "manage_doctors"
    MANAGE_SCHEDULES = "manage_schedules"
    MANAGE_APPOINTMENTS = "manage_appointments"
    MANAGE_ANNOUNCEMENTS = "manage_announcements"
    MANAGE_ADDRESS = "manage_address"
    MANAGE_SUPPORT = "manage_support"
    MANAGE_ADMINS = "manage_admins"
    MANAGE_SETTINGS = "manage_settings"
    VIEW_STATS = "view_stats"
    BROADCAST = "broadcast"


ADMIN_PERMISSIONS: frozenset[Permission] = frozenset(
    {
        Permission.MANAGE_SPECIALTIES,
        Permission.MANAGE_DOCTORS,
        Permission.MANAGE_SCHEDULES,
        Permission.MANAGE_APPOINTMENTS,
        Permission.MANAGE_ANNOUNCEMENTS,
        Permission.MANAGE_ADDRESS,
        Permission.MANAGE_SUPPORT,
        Permission.MANAGE_SETTINGS,
        Permission.VIEW_STATS,
        Permission.BROADCAST,
    }
)

SUPERADMIN_PERMISSIONS: frozenset[Permission] = ADMIN_PERMISSIONS | frozenset(
    {Permission.MANAGE_ADMINS}
)


def get_role(admin) -> AdminRole:
    if admin.is_superadmin:
        return AdminRole.SUPERADMIN
    return AdminRole.ADMIN


def get_permissions(admin) -> frozenset[Permission]:
    if admin.is_superadmin:
        return SUPERADMIN_PERMISSIONS
    return ADMIN_PERMISSIONS


def has_permission(admin, permission: Permission) -> bool:
    return permission in get_permissions(admin)


def role_label(admin) -> str:
    return "⭐ سوپرادمین" if admin.is_superadmin else "👤 ادمین"
