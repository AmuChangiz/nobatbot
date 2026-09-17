from app.bot.bale_compat import CallbackQuery, Command, F, FSMContext, Message, Router
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.admin import IsAdminFilter
from app.bot.keyboards.admin import admin_menu_keyboard
from app.bot.keyboards.common import main_menu_keyboard
from app.bot.permissions import role_label
from app.bot.texts import fa as t
from app.db.models import Admin

router = Router(name="admin_panel")
router.message.filter(IsAdminFilter())
router.callback_query.filter(IsAdminFilter())


@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext, db_admin: Admin) -> None:
    await state.clear()
    await message.answer(
        t.ADMIN_MENU.format(role=role_label(db_admin)),
        reply_markup=admin_menu_keyboard(db_admin),
    )


@router.message(F.text == t.BTN_ADMIN_EXIT)
async def exit_admin(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(t.MAIN_MENU, reply_markup=main_menu_keyboard())


@router.callback_query(F.data == "adm_back")
async def admin_back(callback: CallbackQuery, state: FSMContext, db_admin: Admin) -> None:
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        t.ADMIN_MENU.format(role=role_label(db_admin)),
        reply_markup=admin_menu_keyboard(db_admin),
    )
    await callback.answer()
