from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.bale_compat.types import CallbackQuery, Message
from app.services import AdminService


class IsAdminFilter:
    async def __call__(
        self,
        event: Message | CallbackQuery,
        session: AsyncSession,
    ) -> bool:
        user_id: int | None = None
        if isinstance(event, Message) and event.from_user:
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery) and event.from_user:
            user_id = event.from_user.id

        if user_id is None:
            return False
        return await AdminService.is_admin(session, user_id)
