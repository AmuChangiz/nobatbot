from app.bot.keyboards.markup import build_inline
from app.bot.bale_compat import CallbackQuery, F, FSMContext, Message, Router
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.admin import IsAdminFilter
from app.bot.filters.permissions import PermissionFilter
from app.bot.permissions import Permission
from app.bot.states import AdminContentStates
from app.bot.texts import fa as t
from app.services import SettingsService

router = Router(name="admin_support")
router.message.filter(IsAdminFilter(), PermissionFilter(Permission.MANAGE_SUPPORT))
router.callback_query.filter(IsAdminFilter(), PermissionFilter(Permission.MANAGE_SUPPORT))


def _support_kb():
    return build_inline([
        [(t.BTN_EDIT_SUPPORT, "adm_sup_edit")],
        [(t.BTN_BACK, "adm_back")],
    ])


@router.message(F.text == t.BTN_ADMIN_SUPPORT)
async def show_support_admin(message: Message, session: AsyncSession) -> None:
    current = await SettingsService.get_support(session)
    await message.answer(t.SUPPORT_ADMIN_HEADER.format(current=current), reply_markup=_support_kb())


@router.callback_query(F.data == "adm_sup_edit")
async def edit_support_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminContentStates.enter_support)
    await callback.message.edit_text(t.ENTER_NEW_SUPPORT)
    await callback.answer()


@router.message(AdminContentStates.enter_support, F.text)
async def save_support(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await SettingsService.set(session, SettingsService.SUPPORT_KEY, message.text.strip())
    await state.clear()
    current = await SettingsService.get_support(session)
    await message.answer(t.SUPPORT_UPDATED)
    await message.answer(t.SUPPORT_ADMIN_HEADER.format(current=current), reply_markup=_support_kb())
