from app.bot.bale_compat import Bot, F, FSMContext, Message, Router
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.admin import IsAdminFilter
from app.bot.filters.permissions import PermissionFilter
from app.bot.keyboards.common import confirm_keyboard
from app.bot.permissions import Permission
from app.bot.states import AdminBroadcastStates
from app.bot.texts import fa as t
from app.db.models import Admin
from app.scheduler.broadcast_worker import BroadcastWorker
from app.services import BroadcastService

router = Router(name="admin_broadcast")
router.message.filter(IsAdminFilter(), PermissionFilter(Permission.BROADCAST))
router.callback_query.filter(IsAdminFilter(), PermissionFilter(Permission.BROADCAST))


@router.message(F.text == t.BTN_ADMIN_BROADCAST)
async def broadcast_start(message: Message, state: FSMContext) -> None:
    await state.set_state(AdminBroadcastStates.enter_message)
    await message.answer(t.ENTER_BROADCAST_MESSAGE)


@router.message(AdminBroadcastStates.enter_message, F.text)
async def broadcast_enter_message(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user_ids = await BroadcastService.get_all_user_bale_ids(session)
    await state.update_data(broadcast_message=message.text.strip(), user_count=len(user_ids))
    await state.set_state(AdminBroadcastStates.confirm)
    await message.answer(
        t.CONFIRM_BROADCAST.format(count=len(user_ids), message=message.text.strip()),
        reply_markup=confirm_keyboard(),
    )


@router.message(AdminBroadcastStates.confirm, F.text == t.BTN_CONFIRM)
async def broadcast_confirm(
    message: Message,
    state: FSMContext,
    bot: Bot,
    db_admin: Admin,
) -> None:
    data = await state.get_data()
    text = data["broadcast_message"]
    await state.clear()

    await message.answer(t.BROADCAST_STARTED)
    BroadcastWorker.schedule(
        bot,
        message_text=text,
        admin_bale_user_id=message.from_user.id,
        admin_db_id=db_admin.id,
    )


@router.message(AdminBroadcastStates.confirm, F.text == t.BTN_CANCEL)
async def broadcast_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(t.OPERATION_CANCELLED)
