from app.bot.bale_compat.types import CallbackQuery, Message
from app.bot.permissions import Permission, has_permission
from app.db.models import Admin


class PermissionFilter:
    def __init__(self, permission: Permission) -> None:
        self.permission = permission

    async def __call__(
        self,
        event: Message | CallbackQuery,
        db_admin: Admin | None = None,
    ) -> bool:
        if db_admin is None:
            return False
        return has_permission(db_admin, self.permission)
