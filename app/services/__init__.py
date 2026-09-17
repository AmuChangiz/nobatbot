from dataclasses import dataclass
from datetime import date, datetime, time, timedelta

from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import get_settings
from app.db.models import (
    Admin,
    Appointment,
    AppointmentStatus,
    Doctor,
    Schedule,
    SlotLock,
    Specialty,
    User,
)
from app.utils import day_bounds_db, generate_slots, is_slot_in_past, now_db, today_local


@dataclass
class AvailableSlot:
    schedule_id: int
    doctor_id: int
    schedule_date: date
    slot_time: time


class UserService:
    @staticmethod
    async def get_or_create(
        session: AsyncSession,
        bale_user_id: int,
        full_name: str | None = None,
        username: str | None = None,
    ) -> User:
        result = await session.execute(
            select(User).where(User.bale_user_id == bale_user_id)
        )
        user = result.scalar_one_or_none()
        if user is None:
            user = User(
                bale_user_id=bale_user_id,
                full_name=full_name,
                username=username,
            )
            session.add(user)
            await session.flush()
        else:
            if full_name and user.full_name != full_name:
                user.full_name = full_name
            if username and user.username != username:
                user.username = username
        return user


class AdminService:
    @staticmethod
    async def is_admin(session: AsyncSession, bale_user_id: int) -> bool:
        result = await session.execute(
            select(Admin.id).where(
                Admin.bale_user_id == bale_user_id,
                Admin.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def get_admin(session: AsyncSession, bale_user_id: int) -> Admin | None:
        result = await session.execute(
            select(Admin).where(
                Admin.bale_user_id == bale_user_id,
                Admin.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def bootstrap_superadmins(session: AsyncSession) -> None:
        settings = get_settings()
        for bale_user_id in settings.superadmin_ids:
            result = await session.execute(
                select(Admin).where(Admin.bale_user_id == bale_user_id)
            )
            admin = result.scalar_one_or_none()
            if admin is None:
                session.add(
                    Admin(
                        bale_user_id=bale_user_id,
                        is_superadmin=True,
                        is_active=True,
                    )
                )
            else:
                admin.is_superadmin = True
                admin.is_active = True
        await session.flush()

    @staticmethod
    async def list_admins(session: AsyncSession) -> list[Admin]:
        result = await session.execute(
            select(Admin).where(Admin.is_active.is_(True)).order_by(Admin.id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def add_admin(
        session: AsyncSession,
        bale_user_id: int,
        display_name: str | None = None,
    ) -> Admin:
        result = await session.execute(
            select(Admin).where(Admin.bale_user_id == bale_user_id)
        )
        admin = result.scalar_one_or_none()
        if admin is None:
            admin = Admin(
                bale_user_id=bale_user_id,
                display_name=display_name,
                is_active=True,
            )
            session.add(admin)
        else:
            admin.is_active = True
            if display_name:
                admin.display_name = display_name
        await session.flush()
        return admin

    @staticmethod
    async def remove_admin(session: AsyncSession, admin_id: int) -> bool:
        result = await session.execute(select(Admin).where(Admin.id == admin_id))
        admin = result.scalar_one_or_none()
        if admin is None or admin.is_superadmin:
            return False
        admin.is_active = False
        await session.flush()
        return True

    @staticmethod
    async def set_superadmin(session: AsyncSession, admin_id: int, is_superadmin: bool) -> bool:
        result = await session.execute(select(Admin).where(Admin.id == admin_id))
        admin = result.scalar_one_or_none()
        if admin is None:
            return False
        admin.is_superadmin = is_superadmin
        await session.flush()
        return True


class SpecialtyService:
    @staticmethod
    async def list_active(session: AsyncSession) -> list[Specialty]:
        result = await session.execute(
            select(Specialty)
            .where(Specialty.is_active.is_(True))
            .order_by(Specialty.sort_order, Specialty.name)
        )
        return list(result.scalars().all())

    @staticmethod
    async def list_all(session: AsyncSession) -> list[Specialty]:
        result = await session.execute(
            select(Specialty).order_by(Specialty.sort_order, Specialty.name)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get(session: AsyncSession, specialty_id: int) -> Specialty | None:
        result = await session.execute(
            select(Specialty).where(Specialty.id == specialty_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(session: AsyncSession, name: str, description: str | None = None) -> Specialty:
        specialty = Specialty(name=name, description=description, is_active=True)
        session.add(specialty)
        await session.flush()
        return specialty

    @staticmethod
    async def update(
        session: AsyncSession,
        specialty_id: int,
        name: str | None = None,
        description: str | None = None,
        is_active: bool | None = None,
    ) -> Specialty | None:
        specialty = await SpecialtyService.get(session, specialty_id)
        if specialty is None:
            return None
        if name is not None:
            specialty.name = name
        if description is not None:
            specialty.description = description
        if is_active is not None:
            specialty.is_active = is_active
        await session.flush()
        return specialty

    @staticmethod
    async def delete(session: AsyncSession, specialty_id: int) -> tuple[bool, str]:
        specialty = await SpecialtyService.get(session, specialty_id)
        if specialty is None:
            return False, "not_found"
        if specialty.doctors:
            specialty.is_active = False
            await session.flush()
            return True, "deactivated"
        await session.delete(specialty)
        await session.flush()
        return True, "deleted"


class DoctorService:
    @staticmethod
    async def list_by_specialty(session: AsyncSession, specialty_id: int) -> list[Doctor]:
        result = await session.execute(
            select(Doctor)
            .where(Doctor.specialty_id == specialty_id, Doctor.is_active.is_(True))
            .order_by(Doctor.name)
        )
        return list(result.scalars().all())

    @staticmethod
    async def list_all(session: AsyncSession) -> list[Doctor]:
        result = await session.execute(
            select(Doctor)
            .options(selectinload(Doctor.specialty))
            .order_by(Doctor.name)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get(session: AsyncSession, doctor_id: int) -> Doctor | None:
        result = await session.execute(
            select(Doctor)
            .options(selectinload(Doctor.specialty))
            .where(Doctor.id == doctor_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        session: AsyncSession,
        specialty_id: int,
        name: str,
        bio: str | None = None,
    ) -> Doctor:
        doctor = Doctor(
            specialty_id=specialty_id,
            name=name,
            bio=bio,
            is_active=True,
        )
        session.add(doctor)
        await session.flush()
        return doctor

    @staticmethod
    async def update(
        session: AsyncSession,
        doctor_id: int,
        name: str | None = None,
        bio: str | None = None,
        is_active: bool | None = None,
        specialty_id: int | None = None,
    ) -> Doctor | None:
        doctor = await DoctorService.get(session, doctor_id)
        if doctor is None:
            return None
        if name is not None:
            doctor.name = name
        if bio is not None:
            doctor.bio = bio
        if is_active is not None:
            doctor.is_active = is_active
        if specialty_id is not None:
            doctor.specialty_id = specialty_id
        await session.flush()
        return doctor

    @staticmethod
    async def delete(session: AsyncSession, doctor_id: int) -> tuple[bool, str]:
        doctor = await DoctorService.get(session, doctor_id)
        if doctor is None:
            return False, "not_found"
        doctor.is_active = False
        await session.flush()
        return True, "deactivated"


class ScheduleService:
    @staticmethod
    async def create(
        session: AsyncSession,
        doctor_id: int,
        schedule_date: date,
        start_time: time,
        end_time: time,
        visit_duration_minutes: int,
    ) -> Schedule:
        schedule = Schedule(
            doctor_id=doctor_id,
            schedule_date=schedule_date,
            start_time=start_time,
            end_time=end_time,
            visit_duration_minutes=visit_duration_minutes,
        )
        session.add(schedule)
        await session.flush()
        return schedule

    @staticmethod
    async def get(session: AsyncSession, schedule_id: int) -> Schedule | None:
        result = await session.execute(
            select(Schedule)
            .options(selectinload(Schedule.doctor).selectinload(Doctor.specialty))
            .where(Schedule.id == schedule_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_doctor(session: AsyncSession, doctor_id: int) -> list[Schedule]:
        result = await session.execute(
            select(Schedule)
            .where(Schedule.doctor_id == doctor_id, Schedule.schedule_date >= today_local())
            .order_by(Schedule.schedule_date)
        )
        return list(result.scalars().all())

    @staticmethod
    async def list_future_by_doctor(session: AsyncSession, doctor_id: int) -> list[Schedule]:
        return await ScheduleService.list_by_doctor(session, doctor_id)

    @staticmethod
    async def delete(session: AsyncSession, schedule_id: int) -> bool:
        schedule = await ScheduleService.get(session, schedule_id)
        if schedule is None:
            return False
        await session.delete(schedule)
        await session.flush()
        return True

    @staticmethod
    async def cleanup_past_without_appointments(session: AsyncSession) -> int:
        """Remove past-day schedules that have no booked appointments."""
        from app.db.models import Appointment

        today = today_local()
        booked_subq = select(Appointment.schedule_id).distinct()
        result = await session.execute(
            delete(Schedule).where(
                Schedule.schedule_date < today,
                Schedule.id.not_in(booked_subq),
            )
        )
        await session.flush()
        return result.rowcount or 0

    @staticmethod
    async def update(
        session: AsyncSession,
        schedule_id: int,
        schedule_date: date | None = None,
        start_time: time | None = None,
        end_time: time | None = None,
        visit_duration_minutes: int | None = None,
    ) -> Schedule | None:
        schedule = await ScheduleService.get(session, schedule_id)
        if schedule is None:
            return None
        if schedule_date is not None:
            schedule.schedule_date = schedule_date
        if start_time is not None:
            schedule.start_time = start_time
        if end_time is not None:
            schedule.end_time = end_time
        if visit_duration_minutes is not None:
            schedule.visit_duration_minutes = visit_duration_minutes
        await session.flush()
        return schedule


class SlotService:
    @staticmethod
    async def cleanup_expired_locks(session: AsyncSession) -> int:
        result = await session.execute(
            delete(SlotLock)
            .where(SlotLock.locked_until <= now_db())
            .execution_options(synchronize_session=False)
        )
        return result.rowcount or 0

    @staticmethod
    async def get_available_slots_for_doctor(
        session: AsyncSession,
        doctor_id: int,
    ) -> list[AvailableSlot]:
        await SlotService.cleanup_expired_locks(session)

        schedules = await ScheduleService.list_future_by_doctor(session, doctor_id)
        if not schedules:
            return []

        schedule_ids = [s.id for s in schedules]
        booked_result = await session.execute(
            select(Appointment.schedule_id, Appointment.slot_time).where(
                Appointment.schedule_id.in_(schedule_ids),
                Appointment.status == AppointmentStatus.CONFIRMED,
            )
        )
        booked = {(row.schedule_id, row.slot_time) for row in booked_result.all()}

        locked_result = await session.execute(
            select(SlotLock.schedule_id, SlotLock.slot_time).where(
                SlotLock.schedule_id.in_(schedule_ids),
                SlotLock.locked_until > now_db(),
            )
        )
        locked = {(row.schedule_id, row.slot_time) for row in locked_result.all()}

        available: list[AvailableSlot] = []
        for schedule in schedules:
            slots = generate_slots(
                schedule.schedule_date,
                schedule.start_time,
                schedule.end_time,
                schedule.visit_duration_minutes,
            )
            for slot in slots:
                if is_slot_in_past(schedule.schedule_date, slot):
                    continue
                key = (schedule.id, slot)
                if key in booked or key in locked:
                    continue
                available.append(
                    AvailableSlot(
                        schedule_id=schedule.id,
                        doctor_id=doctor_id,
                        schedule_date=schedule.schedule_date,
                        slot_time=slot,
                    )
                )
        return available

    @staticmethod
    async def get_available_dates_for_doctor(
        session: AsyncSession,
        doctor_id: int,
    ) -> list[date]:
        slots = await SlotService.get_available_slots_for_doctor(session, doctor_id)
        dates = sorted({s.schedule_date for s in slots})
        return dates

    @staticmethod
    async def get_available_slots_for_date(
        session: AsyncSession,
        doctor_id: int,
        schedule_date: date,
    ) -> list[AvailableSlot]:
        all_slots = await SlotService.get_available_slots_for_doctor(session, doctor_id)
        return [s for s in all_slots if s.schedule_date == schedule_date]

    @staticmethod
    async def lock_slot(
        session: AsyncSession,
        user_id: int,
        schedule_id: int,
        slot_time: time,
    ) -> bool:
        await SlotService.cleanup_expired_locks(session)
        await SlotService.release_user_locks(session, user_id)

        schedule = await ScheduleService.get(session, schedule_id)
        if schedule is None:
            return False

        if is_slot_in_past(schedule.schedule_date, slot_time):
            return False

        booked_result = await session.execute(
            select(Appointment.id).where(
                Appointment.schedule_id == schedule_id,
                Appointment.slot_time == slot_time,
                Appointment.status == AppointmentStatus.CONFIRMED,
            )
        )
        if booked_result.scalar_one_or_none() is not None:
            return False

        locked_result = await session.execute(
            select(SlotLock).where(
                SlotLock.schedule_id == schedule_id,
                SlotLock.slot_time == slot_time,
                SlotLock.locked_until > now_db(),
            )
        )
        if locked_result.scalar_one_or_none() is not None:
            return False

        ttl = get_settings().slot_lock_ttl_seconds
        session.add(
            SlotLock(
                user_id=user_id,
                doctor_id=schedule.doctor_id,
                schedule_id=schedule_id,
                slot_time=slot_time,
                locked_until=now_db() + timedelta(seconds=ttl),
            )
        )
        await session.flush()
        return True

    @staticmethod
    async def release_user_locks(session: AsyncSession, user_id: int) -> None:
        await session.execute(delete(SlotLock).where(SlotLock.user_id == user_id))
        await session.flush()

    @staticmethod
    async def release_slot_lock(
        session: AsyncSession,
        user_id: int,
        schedule_id: int,
        slot_time: time,
    ) -> None:
        await session.execute(
            delete(SlotLock).where(
                SlotLock.user_id == user_id,
                SlotLock.schedule_id == schedule_id,
                SlotLock.slot_time == slot_time,
            )
        )
        await session.flush()


class AppointmentService:
    @staticmethod
    async def book(
        session: AsyncSession,
        user_id: int,
        schedule_id: int,
        slot_time: time,
        patient_name: str,
        patient_phone: str,
        appointment_type: str = "in_person",
    ) -> Appointment | None:
        from sqlalchemy.exc import IntegrityError

        from app.utils.tracking_code import generate_tracking_code

        locked = await SlotService.lock_slot(session, user_id, schedule_id, slot_time)
        if not locked:
            return None

        schedule = await ScheduleService.get(session, schedule_id)
        if schedule is None:
            return None

        tracking_code = await generate_tracking_code(session)

        appointment = Appointment(
            user_id=user_id,
            doctor_id=schedule.doctor_id,
            schedule_id=schedule_id,
            slot_time=slot_time,
            status=AppointmentStatus.CONFIRMED,
            patient_name=patient_name,
            patient_phone=patient_phone,
            appointment_type=appointment_type,
            tracking_code=tracking_code,
        )
        try:
            async with session.begin_nested():
                session.add(appointment)
                await session.flush()
        except IntegrityError:
            return None

        await SlotService.release_slot_lock(session, user_id, schedule_id, slot_time)
        return appointment

    @staticmethod
    async def get_user_appointments(
        session: AsyncSession,
        user_id: int,
        include_past: bool = False,
    ) -> list[Appointment]:
        query = (
            select(Appointment)
            .options(
                selectinload(Appointment.doctor).selectinload(Doctor.specialty),
                selectinload(Appointment.schedule),
            )
            .where(Appointment.user_id == user_id)
            .order_by(Appointment.created_at.desc())
        )
        if not include_past:
            query = query.where(Appointment.status == AppointmentStatus.CONFIRMED)

        result = await session.execute(query)
        appointments = list(result.scalars().all())

        if not include_past:
            appointments = [
                a
                for a in appointments
                if not is_slot_in_past(a.schedule.schedule_date, a.slot_time)
            ]
        return appointments

    @staticmethod
    async def get(session: AsyncSession, appointment_id: int) -> Appointment | None:
        result = await session.execute(
            select(Appointment)
            .options(
                selectinload(Appointment.doctor).selectinload(Doctor.specialty),
                selectinload(Appointment.schedule),
                selectinload(Appointment.user),
            )
            .where(Appointment.id == appointment_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def cancel(session: AsyncSession, appointment_id: int, user_id: int) -> bool:
        appointment = await AppointmentService.get(session, appointment_id)
        if appointment is None:
            return False
        if appointment.user_id != user_id:
            return False
        if appointment.status != AppointmentStatus.CONFIRMED:
            return False
        appointment.status = AppointmentStatus.CANCELLED
        appointment.cancelled_at = now_db()
        await session.flush()
        return True

    @staticmethod
    async def get_pending_reminders(session: AsyncSession, hours_before: int) -> list[Appointment]:
        flag_col = (
            Appointment.reminder_24h_sent
            if hours_before >= 12
            else Appointment.reminder_2h_sent
        )
        result = await session.execute(
            select(Appointment)
            .options(
                selectinload(Appointment.user),
                selectinload(Appointment.doctor).selectinload(Doctor.specialty),
                selectinload(Appointment.schedule),
            )
            .where(
                Appointment.status == AppointmentStatus.CONFIRMED,
                flag_col.is_(False),
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def mark_reminder_24h_sent(session: AsyncSession, appointment_id: int) -> None:
        appointment = await AppointmentService.get(session, appointment_id)
        if appointment:
            appointment.reminder_24h_sent = True
            await session.flush()

    @staticmethod
    async def mark_reminder_2h_sent(session: AsyncSession, appointment_id: int) -> None:
        appointment = await AppointmentService.get(session, appointment_id)
        if appointment:
            appointment.reminder_2h_sent = True
            await session.flush()

    @staticmethod
    async def search(
        session: AsyncSession,
        query: str,
        limit: int = 20,
    ) -> list[Appointment]:
        query = query.strip()
        base = (
            select(Appointment)
            .options(
                selectinload(Appointment.doctor).selectinload(Doctor.specialty),
                selectinload(Appointment.schedule),
                selectinload(Appointment.user),
            )
            .order_by(Appointment.created_at.desc())
            .limit(limit)
        )
        if query.upper().startswith("CLN-"):
            result = await session.execute(
                base.where(Appointment.tracking_code.ilike(f"%{query}%"))
            )
        elif query.isdigit() and len(query) >= 10:
            result = await session.execute(
                base.where(Appointment.patient_phone.contains(query[-10:]))
            )
        else:
            result = await session.execute(
                base.where(
                    or_(
                        Appointment.patient_name.ilike(f"%{query}%"),
                        Appointment.patient_phone.contains(query),
                        Appointment.tracking_code.ilike(f"%{query}%"),
                    )
                )
            )
        return list(result.scalars().all())

    @staticmethod
    async def admin_set_status(
        session: AsyncSession,
        appointment_id: int,
        status: AppointmentStatus,
    ) -> bool:
        appointment = await AppointmentService.get(session, appointment_id)
        if appointment is None:
            return False
        appointment.status = status
        if status == AppointmentStatus.CANCELLED:
            appointment.cancelled_at = now_db()
        await session.flush()
        return True

    @staticmethod
    async def admin_cancel(session: AsyncSession, appointment_id: int) -> bool:
        return await AppointmentService.admin_set_status(
            session, appointment_id, AppointmentStatus.CANCELLED
        )

    @staticmethod
    async def list_recent(session: AsyncSession, limit: int = 15) -> list[Appointment]:
        result = await session.execute(
            select(Appointment)
            .options(
                selectinload(Appointment.doctor).selectinload(Doctor.specialty),
                selectinload(Appointment.schedule),
            )
            .order_by(Appointment.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


class BroadcastService:
    @staticmethod
    async def create_record(
        session: AsyncSession,
        admin_id: int,
        message_text: str,
    ) -> int:
        from app.db.models import BroadcastMessage

        record = BroadcastMessage(
            admin_id=admin_id,
            message_text=message_text,
        )
        session.add(record)
        await session.flush()
        return record.id

    @staticmethod
    async def update_counts(
        session: AsyncSession,
        broadcast_id: int,
        sent_count: int,
        failed_count: int,
    ) -> None:
        from app.db.models import BroadcastMessage

        result = await session.execute(
            select(BroadcastMessage).where(BroadcastMessage.id == broadcast_id)
        )
        record = result.scalar_one_or_none()
        if record:
            record.sent_count = sent_count
            record.failed_count = failed_count
            await session.flush()

    @staticmethod
    async def get_all_user_bale_ids(session: AsyncSession) -> list[int]:
        result = await session.execute(select(User.bale_user_id))
        return list(result.scalars().all())


class ReportService:
    @staticmethod
    async def daily_report(session: AsyncSession, report_date: date) -> dict:
        start, end = day_bounds_db(report_date)

        new_users = await session.scalar(
            select(func.count(User.id)).where(
                User.created_at >= start,
                User.created_at <= end,
            )
        )

        new_appointments = await session.scalar(
            select(func.count(Appointment.id)).where(
                Appointment.created_at >= start,
                Appointment.created_at <= end,
            )
        )

        cancelled = await session.scalar(
            select(func.count(Appointment.id)).where(
                Appointment.cancelled_at >= start,
                Appointment.cancelled_at <= end,
            )
        )

        today_appointments_result = await session.execute(
            select(Appointment)
            .options(
                selectinload(Appointment.doctor),
                selectinload(Appointment.schedule),
            )
            .join(Schedule)
            .where(
                Schedule.schedule_date == report_date,
                Appointment.status == AppointmentStatus.CONFIRMED,
            )
            .order_by(Appointment.slot_time)
        )
        today_appointments = list(today_appointments_result.scalars().all())

        return {
            "date": report_date,
            "new_users": new_users or 0,
            "new_appointments": new_appointments or 0,
            "cancelled_appointments": cancelled or 0,
            "today_appointments": today_appointments,
        }


class SettingsService:
    ADDRESS_KEY = "address_text"
    SUPPORT_KEY = "support_text"

    @staticmethod
    async def get(session: AsyncSession, key: str, default: str = "") -> str:
        from app.db.models import BotSetting

        result = await session.execute(select(BotSetting.value).where(BotSetting.key == key))
        value = result.scalar_one_or_none()
        return value if value is not None else default

    @staticmethod
    async def set(session: AsyncSession, key: str, value: str) -> None:
        from app.db.models import BotSetting

        result = await session.execute(select(BotSetting).where(BotSetting.key == key))
        setting = result.scalar_one_or_none()
        if setting is None:
            session.add(BotSetting(key=key, value=value))
        else:
            setting.value = value
        await session.flush()

    @staticmethod
    async def get_address(session: AsyncSession) -> str:
        from app.bot.texts import fa as t

        return await SettingsService.get(session, SettingsService.ADDRESS_KEY, t.ADDRESS_NOT_SET)

    @staticmethod
    async def get_support(session: AsyncSession) -> str:
        from app.bot.texts import fa as t

        return await SettingsService.get(session, SettingsService.SUPPORT_KEY, t.SUPPORT_NOT_SET)

    @staticmethod
    async def bootstrap_defaults(session: AsyncSession) -> None:
        return


class AnnouncementService:
    @staticmethod
    async def list_all(session: AsyncSession) -> list:
        from app.db.models import Announcement

        result = await session.execute(
            select(Announcement).order_by(Announcement.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def list_active(session: AsyncSession) -> list:
        from app.db.models import Announcement

        result = await session.execute(
            select(Announcement)
            .where(Announcement.is_active.is_(True))
            .order_by(Announcement.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get(session: AsyncSession, announcement_id: int):
        from app.db.models import Announcement

        result = await session.execute(
            select(Announcement).where(Announcement.id == announcement_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        session: AsyncSession,
        title: str,
        content: str,
        admin_id: int | None = None,
    ):
        from app.db.models import Announcement

        item = Announcement(title=title, content=content, admin_id=admin_id, is_active=True)
        session.add(item)
        await session.flush()
        return item

    @staticmethod
    async def update(
        session: AsyncSession,
        announcement_id: int,
        title: str | None = None,
        content: str | None = None,
        is_active: bool | None = None,
    ):
        item = await AnnouncementService.get(session, announcement_id)
        if item is None:
            return None
        if title is not None:
            item.title = title
        if content is not None:
            item.content = content
        if is_active is not None:
            item.is_active = is_active
        await session.flush()
        return item

    @staticmethod
    async def delete(session: AsyncSession, announcement_id: int) -> bool:
        item = await AnnouncementService.get(session, announcement_id)
        if item is None:
            return False
        await session.delete(item)
        await session.flush()
        return True


class StatsService:
    @staticmethod
    async def system_stats(session: AsyncSession) -> dict:
        from app.db.models import Announcement

        total_users = await session.scalar(select(func.count(User.id))) or 0
        total_admins = await session.scalar(
            select(func.count(Admin.id)).where(Admin.is_active.is_(True))
        ) or 0
        total_specialties = await session.scalar(
            select(func.count(Specialty.id)).where(Specialty.is_active.is_(True))
        ) or 0
        total_doctors = await session.scalar(
            select(func.count(Doctor.id)).where(Doctor.is_active.is_(True))
        ) or 0
        total_schedules = await session.scalar(select(func.count(Schedule.id))) or 0
        total_appointments = await session.scalar(select(func.count(Appointment.id))) or 0
        confirmed = await session.scalar(
            select(func.count(Appointment.id)).where(
                Appointment.status == AppointmentStatus.CONFIRMED
            )
        ) or 0
        cancelled = await session.scalar(
            select(func.count(Appointment.id)).where(
                Appointment.status == AppointmentStatus.CANCELLED
            )
        ) or 0
        completed = await session.scalar(
            select(func.count(Appointment.id)).where(
                Appointment.status == AppointmentStatus.COMPLETED
            )
        ) or 0
        announcements = await session.scalar(
            select(func.count(Announcement.id)).where(Announcement.is_active.is_(True))
        ) or 0
        today = today_local()
        today_appts = await session.scalar(
            select(func.count(Appointment.id))
            .join(Schedule)
            .where(
                Schedule.schedule_date == today,
                Appointment.status == AppointmentStatus.CONFIRMED,
            )
        ) or 0

        return {
            "total_users": total_users,
            "total_admins": total_admins,
            "total_specialties": total_specialties,
            "total_doctors": total_doctors,
            "total_schedules": total_schedules,
            "total_appointments": total_appointments,
            "confirmed_appointments": confirmed,
            "cancelled_appointments": cancelled,
            "completed_appointments": completed,
            "active_announcements": announcements,
            "today_appointments": today_appts,
        }
