from app.bot.bale_compat import CallbackQuery, F, FSMContext, Message, Router
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.admin import IsAdminFilter
from app.bot.filters.permissions import PermissionFilter
from app.bot.keyboards.admin import inline_admin_detail, inline_admins_list, inline_confirm_delete
from app.bot.permissions import Permission, role_label
from app.bot.states import AdminManageStates
from app.bot.texts import fa as t
from app.db.models import Admin
from app.services import AdminService

router = Router(name="admin_manage")
router.message.filter(IsAdminFilter(), PermissionFilter(Permission.MANAGE_ADMINS))
router.callback_query.filter(IsAdminFilter(), PermissionFilter(Permission.MANAGE_ADMINS))


@router.message(F.text == t.BTN_ADMIN_ADMINS)
async def list_admins(message: Message, session: AsyncSession, db_admin: Admin) -> None:
    admins = await AdminService.list_admins(session)
    await message.answer(
        t.ADMIN_LIST_HEADER,
        reply_markup=inline_admins_list(admins, db_admin.is_superadmin),
    )


@router.callback_query(F.data == "adm_user_list")
async def cb_list(callback: CallbackQuery, session: AsyncSession, db_admin: Admin) -> None:
    admins = await AdminService.list_admins(session)
    await callback.message.edit_text(
        t.ADMIN_LIST_HEADER,
        reply_markup=inline_admins_list(admins, db_admin.is_superadmin),
    )
    await callback.answer()


@router.callback_query(F.data == "adm_add")
async def add_admin_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminManageStates.enter_bale_user_id)
    await callback.message.edit_text(t.ENTER_ADMIN_ID)
    await callback.answer()


@router.message(AdminManageStates.enter_bale_user_id, F.text)
async def add_admin_id(message: Message, state: FSMContext) -> None:
    if not message.text.strip().isdigit():
        await message.answer("شناسه بله باید عدد باشد.")
        return
    await state.update_data(bale_user_id=int(message.text.strip()))
    await state.set_state(AdminManageStates.enter_display_name)
    await message.answer(t.ENTER_ADMIN_NAME)


@router.message(AdminManageStates.enter_display_name, F.text)
async def add_admin_name(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    bale_user_id = data["bale_user_id"]
    display_name = None if message.text == "/skip" else message.text.strip()

    existing = await AdminService.get_admin(session, bale_user_id)
    if existing and existing.is_active:
        await state.clear()
        await message.answer(t.ADMIN_EXISTS)
        return

    await AdminService.add_admin(session, bale_user_id, display_name)
    await state.clear()
    admins = await AdminService.list_admins(session)
    await message.answer(t.ADMIN_ADDED, reply_markup=inline_admins_list(admins, True))


@router.callback_query(F.data.startswith("adm_user:"))
async def view_admin(callback: CallbackQuery, session: AsyncSession, db_admin: Admin) -> None:
    admin_id = int(callback.data.split(":")[1])
    admin = (await AdminService.list_admins(session))
    target = next((a for a in admin if a.id == admin_id), None)
    if target is None:
        await callback.answer(t.ERROR_GENERIC, show_alert=True)
        return
    text = t.ADMIN_DETAIL.format(
        role=role_label(target),
        bale_user_id=target.bale_user_id,
        name=target.display_name or "—",
        status=t.STATUS_ACTIVE if target.is_active else t.STATUS_INACTIVE,
    )
    await callback.message.edit_text(
        text,
        reply_markup=inline_admin_detail(admin_id, db_admin.is_superadmin, target.is_superadmin),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm_promote:"))
async def promote_admin(callback: CallbackQuery, session: AsyncSession, db_admin: Admin) -> None:
    if not db_admin.is_superadmin:
        await callback.answer(t.PERMISSION_DENIED, show_alert=True)
        return
    admin_id = int(callback.data.split(":")[1])
    await AdminService.set_superadmin(session, admin_id, True)
    await callback.answer(t.ADMIN_PROMOTED)
    await cb_list(callback, session, db_admin)


@router.callback_query(F.data.startswith("adm_demote:"))
async def demote_admin(callback: CallbackQuery, session: AsyncSession, db_admin: Admin) -> None:
    if not db_admin.is_superadmin:
        await callback.answer(t.PERMISSION_DENIED, show_alert=True)
        return
    admin_id = int(callback.data.split(":")[1])
    if admin_id == db_admin.id:
        await callback.answer("نمی‌توانید خود را تنزل دهید.", show_alert=True)
        return
    await AdminService.set_superadmin(session, admin_id, False)
    await callback.answer(t.ADMIN_DEMOTED)
    await cb_list(callback, session, db_admin)


@router.callback_query(F.data.startswith("adm_user_del:"))
async def delete_admin_confirm(callback: CallbackQuery, session: AsyncSession) -> None:
    admin_id = int(callback.data.split(":")[1])
    admins = await AdminService.list_admins(session)
    target = next((a for a in admins if a.id == admin_id), None)
    if target is None:
        await callback.answer(t.ERROR_GENERIC, show_alert=True)
        return
    name = target.display_name or str(target.bale_user_id)
    await callback.message.edit_text(
        t.CONFIRM_DELETE.format(name=name),
        reply_markup=inline_confirm_delete("admin", admin_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm_del_yes:admin:"))
async def delete_admin_yes(callback: CallbackQuery, session: AsyncSession, db_admin: Admin) -> None:
    admin_id = int(callback.data.split(":")[2])
    if admin_id == db_admin.id:
        await callback.answer("نمی‌توانید خود را حذف کنید.", show_alert=True)
        return
    if not await AdminService.remove_admin(session, admin_id):
        await callback.answer(t.CANNOT_REMOVE_SUPERADMIN, show_alert=True)
        return
    await callback.message.edit_text(t.ADMIN_REMOVED)
    admins = await AdminService.list_admins(session)
    await callback.message.answer(
        t.ADMIN_LIST_HEADER,
        reply_markup=inline_admins_list(admins, db_admin.is_superadmin),
    )
    await callback.answer()
