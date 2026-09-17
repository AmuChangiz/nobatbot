from app.bot.bale_compat import CallbackQuery, F, FSMContext, Message, Router
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters.admin import IsAdminFilter
from app.bot.filters.permissions import PermissionFilter
from app.bot.keyboards.admin import (
    inline_confirm_delete,
    inline_doctor_detail,
    inline_doctors_admin,
    inline_specialties_pick,
)
from app.bot.permissions import Permission
from app.bot.states import AdminDoctorStates
from app.bot.texts import fa as t
from app.services import DoctorService, SpecialtyService

router = Router(name="admin_doctor")
router.message.filter(IsAdminFilter(), PermissionFilter(Permission.MANAGE_DOCTORS))
router.callback_query.filter(IsAdminFilter(), PermissionFilter(Permission.MANAGE_DOCTORS))


@router.message(F.text == t.BTN_ADMIN_DOCTORS)
async def list_doctors(message: Message, session: AsyncSession) -> None:
    doctors = await DoctorService.list_all(session)
    await message.answer(t.DOCTOR_LIST_HEADER, reply_markup=inline_doctors_admin(doctors))


@router.callback_query(F.data == "adm_doc_list")
async def cb_list_doctors(callback: CallbackQuery, session: AsyncSession) -> None:
    doctors = await DoctorService.list_all(session)
    await callback.message.edit_text(t.DOCTOR_LIST_HEADER, reply_markup=inline_doctors_admin(doctors))
    await callback.answer()


@router.callback_query(F.data == "adm_doc_add")
async def add_doctor_start(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    specialties = await SpecialtyService.list_active(session)
    if not specialties:
        await callback.answer("ابتدا یک تخصص فعال ایجاد کنید.", show_alert=True)
        return
    await state.update_data(edit_id=None)
    await state.set_state(AdminDoctorStates.select_specialty)
    await callback.message.edit_text(t.SELECT_SPECIALTY_FOR_DOCTOR, reply_markup=inline_specialties_pick(specialties, "adm_doc_new_spec"))
    await callback.answer()


@router.callback_query(AdminDoctorStates.select_specialty, F.data.startswith("adm_doc_new_spec:"))
async def add_doctor_specialty(callback: CallbackQuery, state: FSMContext) -> None:
    specialty_id = int(callback.data.split(":")[1])
    await state.update_data(specialty_id=specialty_id)
    await state.set_state(AdminDoctorStates.enter_name)
    await callback.message.edit_text(t.ENTER_DOCTOR_NAME)
    await callback.answer()


@router.message(AdminDoctorStates.enter_name, F.text)
async def add_doctor_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text.strip())
    await state.set_state(AdminDoctorStates.enter_bio)
    await message.answer(t.ENTER_DOCTOR_BIO)


@router.message(AdminDoctorStates.enter_bio, F.text)
async def add_doctor_bio(message: Message, state: FSMContext, session: AsyncSession) -> None:
    bio = None if message.text == "/skip" else message.text.strip()
    data = await state.get_data()
    doctor = await DoctorService.create(session, data["specialty_id"], data["name"], bio)
    await state.clear()
    await message.answer(
        t.DOCTOR_CREATED.format(name=doctor.name),
        reply_markup=inline_doctors_admin(await DoctorService.list_all(session)),
    )


@router.callback_query(F.data.startswith("adm_doc:"))
async def view_doctor(callback: CallbackQuery, session: AsyncSession) -> None:
    doctor_id = int(callback.data.split(":")[1])
    doctor = await DoctorService.get(session, doctor_id)
    if doctor is None:
        await callback.answer(t.ERROR_GENERIC, show_alert=True)
        return
    text = f"👨‍⚕️ {doctor.name}\nتخصص: {doctor.specialty.name}\n"
    if doctor.bio:
        text += f"\n{doctor.bio}\n"
    text += f"\nوضعیت: {'فعال' if doctor.is_active else 'غیرفعال'}"
    await callback.message.edit_text(text, reply_markup=inline_doctor_detail(doctor_id))
    await callback.answer()


@router.callback_query(F.data.startswith("adm_doc_edit:"))
async def edit_doctor_start(callback: CallbackQuery, state: FSMContext) -> None:
    doctor_id = int(callback.data.split(":")[1])
    await state.update_data(edit_id=doctor_id)
    await state.set_state(AdminDoctorStates.edit_name)
    await callback.message.edit_text(t.ENTER_DOCTOR_EDIT_NAME)
    await callback.answer()


@router.message(AdminDoctorStates.edit_name, F.text)
async def edit_doctor_name(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    await DoctorService.update(session, data["edit_id"], name=message.text.strip())
    await state.set_state(AdminDoctorStates.edit_bio)
    await message.answer(t.ENTER_DOCTOR_EDIT_BIO)


@router.message(AdminDoctorStates.edit_bio, F.text)
async def edit_doctor_bio(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    bio = None if message.text == "/skip" else message.text.strip()
    await DoctorService.update(session, data["edit_id"], bio=bio)
    specialties = await SpecialtyService.list_active(session)
    await state.set_state(AdminDoctorStates.edit_specialty)
    await message.answer(t.SELECT_DOCTOR_EDIT_SPECIALTY, reply_markup=inline_specialties_pick(specialties, "adm_doc_edit_spec"))


@router.callback_query(AdminDoctorStates.edit_specialty, F.data.startswith("adm_doc_edit_spec:"))
async def edit_doctor_specialty(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    specialty_id = int(callback.data.split(":")[1])
    data = await state.get_data()
    await DoctorService.update(session, data["edit_id"], specialty_id=specialty_id)
    await state.clear()
    await callback.message.edit_text(t.DOCTOR_UPDATED)
    await callback.message.answer(
        t.DOCTOR_LIST_HEADER,
        reply_markup=inline_doctors_admin(await DoctorService.list_all(session)),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm_toggle:doc:"))
async def toggle_doctor(callback: CallbackQuery, session: AsyncSession) -> None:
    doctor_id = int(callback.data.split(":")[2])
    doctor = await DoctorService.get(session, doctor_id)
    if doctor is None:
        await callback.answer(t.ERROR_GENERIC, show_alert=True)
        return
    await DoctorService.update(session, doctor_id, is_active=not doctor.is_active)
    await callback.answer(t.DOCTOR_UPDATED)
    doctors = await DoctorService.list_all(session)
    await callback.message.edit_text(t.DOCTOR_LIST_HEADER, reply_markup=inline_doctors_admin(doctors))


@router.callback_query(F.data.startswith("adm_doc_del:"))
async def delete_doctor_confirm(callback: CallbackQuery, session: AsyncSession) -> None:
    doctor_id = int(callback.data.split(":")[1])
    doctor = await DoctorService.get(session, doctor_id)
    if doctor is None:
        await callback.answer(t.ERROR_GENERIC, show_alert=True)
        return
    await callback.message.edit_text(
        t.CONFIRM_DELETE.format(name=doctor.name),
        reply_markup=inline_confirm_delete("doc", doctor_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("adm_del_yes:doc:"))
async def delete_doctor_yes(callback: CallbackQuery, session: AsyncSession) -> None:
    doctor_id = int(callback.data.split(":")[2])
    await DoctorService.delete(session, doctor_id)
    await callback.message.edit_text(t.DOCTOR_DELETED)
    await callback.message.answer(
        t.DOCTOR_LIST_HEADER,
        reply_markup=inline_doctors_admin(await DoctorService.list_all(session)),
    )
    await callback.answer()
