from app.bot.bale_compat import F, Message, Router
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.keyboards.common import main_menu_keyboard
from app.bot.texts import fa as t
from app.services import AnnouncementService, SettingsService

router = Router(name="menu")


@router.message(F.text == t.BTN_ADDRESS)
async def show_address(message: Message, session: AsyncSession) -> None:
    text = await SettingsService.get_address(session)
    await message.answer(text, reply_markup=main_menu_keyboard())


@router.message(F.text == t.BTN_SUPPORT)
async def show_support(message: Message, session: AsyncSession) -> None:
    text = await SettingsService.get_support(session)
    announcements = await AnnouncementService.list_active(session)
    if announcements:
        parts = [text, "", "📣 اعلامیه‌ها:", ""]
        for ann in announcements[:3]:
            parts.append(f"• {ann.title}\n{ann.content}")
        text = "\n".join(parts)
    await message.answer(text, reply_markup=main_menu_keyboard())
