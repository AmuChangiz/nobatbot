from app.bot.bale_compat import Command, CommandStart, F, FSMContext, Message, Router
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.common import main_menu_keyboard
from app.bot.keyboards.user import inline_resume_booking
from app.bot.texts import fa as t
from app.db.models import User
from app.services import SlotService

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    db_user: User,
) -> None:
    current = await state.get_state()
    if current and current.startswith("BookingStates"):
        await message.answer(
            f"سلام {db_user.full_name or 'کاربر گرامی'}! 👋\n\n{t.BOOKING_IN_PROGRESS}",
            reply_markup=inline_resume_booking(),
        )
        return

    await state.clear()
    await message.answer(
        f"سلام {db_user.full_name or 'کاربر گرامی'}! 👋\n\n{t.MAIN_MENU}",
        reply_markup=main_menu_keyboard(),
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext, session: AsyncSession, db_user: User) -> None:
    current = await state.get_state()
    if current and current.startswith("BookingStates"):
        await SlotService.release_user_locks(session, db_user.id)
    await state.clear()
    await message.answer(t.MAIN_MENU, reply_markup=main_menu_keyboard())


@router.message(F.text == t.BTN_MAIN_MENU)
async def btn_main_menu(message: Message, state: FSMContext, session: AsyncSession, db_user: User) -> None:
    current = await state.get_state()
    if current and current.startswith("BookingStates"):
        await SlotService.release_user_locks(session, db_user.id)
    await state.clear()
    await message.answer(t.MAIN_MENU, reply_markup=main_menu_keyboard())
