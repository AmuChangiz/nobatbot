from app.bot.bale_compat import CallbackQuery, F, FSMContext, Message, Router
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.admin import IsAdminFilter
from app.bot.filters.permissions import PermissionFilter
from app.bot.keyboards.admin import inline_announcement_detail, inline_announcements_admin, inline_confirm_delete
from app.bot.permissions import Permission
from app.bot.states import AdminAnnouncementStates
from app.bot.texts import fa as t
from app.db.models import Admin
from app.services import AnnouncementService

router = Router(name="admin_announcements")
router.message.filter(IsAdminFilter(), PermissionFilter(Permission.MANAGE_ANNOUNCEMENTS))
router.callback_query.filter(IsAdminFilter(), PermissionFilter(Permission.MANAGE_ANNOUNCEMENTS))


@router.message(F.text == t.BTN_ADMIN_ANNOUNCEMENTS)
async def list_announcements(message: Message, session: AsyncSession) -> None:
    items = await AnnouncementService.list_all(session)
    await message.answer(t.ANNOUNCEMENT_LIST_HEADER, reply_markup=inline_announcements_admin(items))


@router.callback_query(F.data == "adm_ann_list")
async def cb_list(callback: CallbackQuery, session: AsyncSession) -> None:
    items = await AnnouncementService.list_all(session)
    await callback.message.edit_text(t.ANNOUNCEMENT_LIST_HEADER, reply_markup=inline_announcements_admin(items))
    await callback.answer()


@router.callback_query(F.data == "adm_ann_add")
async def add_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(edit_id=None)
    await state.set_state(AdminAnnouncementStates.enter_title)
    await callback.message.edit_text(t.ENTER_ANNOUNCEMENT_TITLE)
    await callback.answer()


@router.message(AdminAnnouncementStates.enter_title, F.text)
async def add_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text.strip())
    await state.set_state(AdminAnnouncementStates.enter_content)
    await message.answer(t.ENTER_ANNOUNCEMENT_CONTENT)


@router.message(AdminAnnouncementStates.enter_content, F.text)
async def add_content(message: Message, state: FSMContext, session: AsyncSession, db_admin: Admin) -> None:
    data = await state.get_data()
    item = await AnnouncementService.create(session, data["title"], message.text.strip(), db_admin.id)
    await state.clear()
    await message.answer(
        t.ANNOUNCEMENT_CREATED.format(title=item.title),
        reply_markup=inline_announcements_admin(await AnnouncementService.list_all(session)),
    )


@router.callback_query(F.data.startswith("adm_ann:"))
async def view_item(callback: CallbackQuery, session: AsyncSession) -> None:
    ann_id = int(callback.data.split(":")[1])
    item = await AnnouncementService.get(session, ann_id)
    if item is None:
        await callback.answer(t.ERROR_GENERIC, show_alert=True)
        return
    text = t.ANNOUNCEMENT_DETAIL.format(
        title=item.title,
        content=item.content,
        status="فعال" if item.is_active else "غیرفعال",
    )
    await callback.message.edit_text(text, reply_markup=inline_announcement_detail(ann_id))
    await callback.answer()


@router.callback_query(F.data.startswith("adm_ann_edit:"))
async def edit_start(callback: CallbackQuery, state: FSMContext) -> None:
    ann_id = int(callback.data.split(":")[1])
    await state.update_data(edit_id=ann_id)
    await state.set_state(AdminAnnouncementStates.edit_title)
    await callback.message.edit_text(t.ENTER_ANNOUNCEMENT_TITLE)
    await callback.answer()


@router.message(AdminAnnouncementStates.edit_title, F.text)
async def edit_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text.strip())
    await state.set_state(AdminAnnouncementStates.edit_content)
    await message.answer(t.ENTER_ANNOUNCEMENT_CONTENT)


@router.message(AdminAnnouncementStates.edit_content, F.text)
async def edit_content(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    await AnnouncementService.update(session, data["edit_id"], title=data["title"], content=message.text.strip())
    await state.clear()
    await message.answer(
        t.ANNOUNCEMENT_UPDATED,
        reply_markup=inline_announcements_admin(await AnnouncementService.list_all(session)),
    )


@router.callback_query(F.data.startswith("adm_ann_toggle:"))
async def toggle_item(callback: CallbackQuery, session: AsyncSession) -> None:
    ann_id = int(callback.data.split(":")[1])
    item = await AnnouncementService.get(session, ann_id)
    if item is None:
        await callback.answer(t.ERROR_GENERIC, show_alert=True)
        return
    await AnnouncementService.update(session, ann_id, is_active=not item.is_active)
    await callback.answer(t.ANNOUNCEMENT_UPDATED)
    items = await AnnouncementService.list_all(session)
    await callback.message.edit_text(t.ANNOUNCEMENT_LIST_HEADER, reply_markup=inline_announcements_admin(items))


@router.callback_query(F.data.startswith("adm_ann_del:"))
async def delete_confirm(callback: CallbackQuery, session: AsyncSession) -> None:
    ann_id = int(callback.data.split(":")[1])
    item = await AnnouncementService.get(session, ann_id)
    if item is None:
        await callback.answer(t.ERROR_GENERIC, show_alert=True)
        return
    await callback.message.edit_text(
        t.CONFIRM_DELETE.format(name=item.title),
        reply_markup=inline_confirm_delete("ann", ann_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm_del_yes:ann:"))
async def delete_yes(callback: CallbackQuery, session: AsyncSession) -> None:
    ann_id = int(callback.data.split(":")[2])
    await AnnouncementService.delete(session, ann_id)
    await callback.message.edit_text(t.ANNOUNCEMENT_DELETED)
    await callback.message.answer(
        t.ANNOUNCEMENT_LIST_HEADER,
        reply_markup=inline_announcements_admin(await AnnouncementService.list_all(session)),
    )
    await callback.answer()
