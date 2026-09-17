from app.bot.keyboards.markup import build_inline
from app.bot.bale_compat import CallbackQuery, F, FSMContext, Message, Router
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.admin import IsAdminFilter
from app.bot.filters.permissions import PermissionFilter
from app.bot.permissions import Permission
from app.bot.states import AdminContentStates
from app.bot.texts import fa as t
from app.services import SettingsService

router = Router(name="admin_address")
router.message.filter(IsAdminFilter(), PermissionFilter(Permission.MANAGE_ADDRESS))
router.callback_query.filter(IsAdminFilter(), PermissionFilter(Permission.MANAGE_ADDRESS))


def _address_kb():
    return build_inline([
        [(t.BTN_EDIT_ADDRESS, "adm_addr_edit")],
        [(t.BTN_BACK, "adm_back")],
    ])


@router.message(F.text == t.BTN_ADMIN_ADDRESS)
async def show_address_admin(message: Message, session: AsyncSession) -> None:
    current = await SettingsService.get_address(session)
    await message.answer(t.ADDRESS_ADMIN_HEADER.format(current=current), reply_markup=_address_kb())


@router.callback_query(F.data == "adm_addr_edit")
async def edit_address_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminContentStates.enter_address)
    await callback.message.edit_text(t.ENTER_NEW_ADDRESS)
    await callback.answer()


@router.message(AdminContentStates.enter_address, F.text)
async def save_address(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await SettingsService.set(session, SettingsService.ADDRESS_KEY, message.text.strip())
    await state.clear()
    current = await SettingsService.get_address(session)
    await message.answer(t.ADDRESS_UPDATED)
    await message.answer(t.ADDRESS_ADMIN_HEADER.format(current=current), reply_markup=_address_kb())
