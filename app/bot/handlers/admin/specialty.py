from app.bot.bale_compat import CallbackQuery, F, FSMContext, Message, Router
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.admin import IsAdminFilter
from app.bot.filters.permissions import PermissionFilter
from app.bot.keyboards.admin import inline_confirm_delete, inline_specialties_admin, inline_specialty_detail
from app.bot.permissions import Permission
from app.bot.states import AdminSpecialtyStates
from app.bot.texts import fa as t
from app.services import SpecialtyService

router = Router(name="admin_specialty")
router.message.filter(IsAdminFilter(), PermissionFilter(Permission.MANAGE_SPECIALTIES))
router.callback_query.filter(IsAdminFilter(), PermissionFilter(Permission.MANAGE_SPECIALTIES))


@router.message(F.text == t.BTN_ADMIN_SPECIALTIES)
async def list_specialties(message: Message, session: AsyncSession) -> None:
    specialties = await SpecialtyService.list_all(session)
    await message.answer(t.SPECIALTY_LIST_HEADER, reply_markup=inline_specialties_admin(specialties))


@router.callback_query(F.data == "adm_spec_list")
async def cb_list_specialties(callback: CallbackQuery, session: AsyncSession) -> None:
    specialties = await SpecialtyService.list_all(session)
    await callback.message.edit_text(t.SPECIALTY_LIST_HEADER, reply_markup=inline_specialties_admin(specialties))
    await callback.answer()


@router.callback_query(F.data == "adm_spec_add")
async def add_specialty_start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdminSpecialtyStates.enter_name)
    await state.update_data(edit_id=None)
    await callback.message.edit_text(t.ENTER_SPECIALTY_NAME)
    await callback.answer()


@router.message(AdminSpecialtyStates.enter_name, F.text)
async def add_specialty_name(message: Message, state: FSMContext) -> None:
    if message.text == t.BTN_CANCEL:
        await state.clear()
        await message.answer(t.OPERATION_CANCELLED)
        return
    await state.update_data(name=message.text.strip())
    await state.set_state(AdminSpecialtyStates.enter_description)
    await message.answer(t.ENTER_SPECIALTY_DESC)


@router.message(AdminSpecialtyStates.enter_description, F.text)
async def add_specialty_description(message: Message, state: FSMContext, session: AsyncSession) -> None:
    description = None if message.text == "/skip" else message.text.strip()
    data = await state.get_data()
    specialty = await SpecialtyService.create(session, data["name"], description)
    await state.clear()
    await message.answer(
        t.SPECIALTY_CREATED.format(name=specialty.name),
        reply_markup=inline_specialties_admin(await SpecialtyService.list_all(session)),
    )


@router.callback_query(F.data.startswith("adm_spec:"))
async def view_specialty(callback: CallbackQuery, session: AsyncSession) -> None:
    specialty_id = int(callback.data.split(":")[1])
    specialty = await SpecialtyService.get(session, specialty_id)
    if specialty is None:
        await callback.answer(t.ERROR_GENERIC, show_alert=True)
        return
    text = f"🏷 {specialty.name}\n"
    if specialty.description:
        text += f"\n{specialty.description}\n"
    text += f"\nوضعیت: {'فعال' if specialty.is_active else 'غیرفعال'}"
    await callback.message.edit_text(text, reply_markup=inline_specialty_detail(specialty_id))
    await callback.answer()


@router.callback_query(F.data.startswith("adm_spec_edit:"))
async def edit_specialty_start(callback: CallbackQuery, state: FSMContext) -> None:
    specialty_id = int(callback.data.split(":")[1])
    await state.update_data(edit_id=specialty_id)
    await state.set_state(AdminSpecialtyStates.edit_name)
    await callback.message.edit_text(t.ENTER_SPECIALTY_EDIT_NAME)
    await callback.answer()


@router.message(AdminSpecialtyStates.edit_name, F.text)
async def edit_specialty_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text.strip())
    await state.set_state(AdminSpecialtyStates.edit_description)
    await message.answer(t.ENTER_SPECIALTY_EDIT_DESC)


@router.message(AdminSpecialtyStates.edit_description, F.text)
async def edit_specialty_description(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    description = None if message.text == "/skip" else message.text.strip()
    await SpecialtyService.update(session, data["edit_id"], name=data["name"], description=description)
    await state.clear()
    await message.answer(
        t.SPECIALTY_UPDATED,
        reply_markup=inline_specialties_admin(await SpecialtyService.list_all(session)),
    )


@router.callback_query(F.data.startswith("adm_toggle:spec:"))
async def toggle_specialty(callback: CallbackQuery, session: AsyncSession) -> None:
    specialty_id = int(callback.data.split(":")[2])
    specialty = await SpecialtyService.get(session, specialty_id)
    if specialty is None:
        await callback.answer(t.ERROR_GENERIC, show_alert=True)
        return
    await SpecialtyService.update(session, specialty_id, is_active=not specialty.is_active)
    await callback.answer(t.SPECIALTY_UPDATED)
    specialties = await SpecialtyService.list_all(session)
    await callback.message.edit_text(t.SPECIALTY_LIST_HEADER, reply_markup=inline_specialties_admin(specialties))


@router.callback_query(F.data.startswith("adm_spec_del:"))
async def delete_specialty_confirm(callback: CallbackQuery, session: AsyncSession) -> None:
    specialty_id = int(callback.data.split(":")[1])
    specialty = await SpecialtyService.get(session, specialty_id)
    if specialty is None:
        await callback.answer(t.ERROR_GENERIC, show_alert=True)
        return
    await callback.message.edit_text(
        t.CONFIRM_DELETE.format(name=specialty.name),
        reply_markup=inline_confirm_delete("spec", specialty_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm_del_yes:spec:"))
async def delete_specialty_yes(callback: CallbackQuery, session: AsyncSession) -> None:
    specialty_id = int(callback.data.split(":")[2])
    ok, result = await SpecialtyService.delete(session, specialty_id)
    if not ok:
        await callback.answer(t.ERROR_GENERIC, show_alert=True)
        return
    msg = t.SPECIALTY_DEACTIVATED if result == "deactivated" else t.SPECIALTY_DELETED
    await callback.message.edit_text(msg)
    await callback.message.answer(
        t.SPECIALTY_LIST_HEADER,
        reply_markup=inline_specialties_admin(await SpecialtyService.list_all(session)),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm_del_no:"))
async def delete_cancel(callback: CallbackQuery) -> None:
    await callback.message.edit_text(t.OPERATION_CANCELLED)
    await callback.answer()
