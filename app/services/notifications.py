import logging
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import TYPE_CHECKING

from app.bot.constants.appointment_types import get_appointment_type_label
from app.bot.texts import fa as t
from app.db.models import Appointment
from app.db.session import get_session_factory
from app.utils import combine_datetime, format_date_persian, format_time, now_tz

if TYPE_CHECKING:
    from app.bot.bale_compat import Bot

logger = logging.getLogger(__name__)


@dataclass
class AppointmentNotifyData:
    tracking_code: str
    patient_name: str
    patient_phone: str
    doctor_name: str
    specialty_name: str
    appointment_type: str
    schedule_date: date
    slot_time: time
    user_bale_id: int

    @classmethod
    def from_appointment(cls, appt: Appointment) -> "AppointmentNotifyData":
        return cls(
            tracking_code=appt.tracking_code,
            patient_name=appt.patient_name,
            patient_phone=appt.patient_phone,
            doctor_name=appt.doctor.name,
            specialty_name=appt.doctor.specialty.name,
            appointment_type=get_appointment_type_label(appt.appointment_type),
            schedule_date=appt.schedule.schedule_date,
            slot_time=appt.slot_time,
            user_bale_id=appt.user.bale_user_id,
        )


class NotificationService:
    @staticmethod
    async def _send_user(bot: "Bot", bale_user_id: int, text: str) -> bool:
        try:
            await bot.send_message(bale_user_id, text)
            return True
        except Exception:
            logger.exception("Failed to send user notification to %d", bale_user_id)
            return False

    @staticmethod
    async def _send_all_admins(bot: "Bot", text: str) -> int:
        from app.services import AdminService

        session_factory = get_session_factory()
        sent = 0
        async with session_factory() as session:
            admins = await AdminService.list_admins(session)
            for admin in admins:
                try:
                    await bot.send_message(admin.bale_user_id, text)
                    sent += 1
                except Exception:
                    logger.exception("Failed to notify admin %d", admin.bale_user_id)
        return sent

    @staticmethod
    async def notify_booking_confirmed(bot: "Bot", appt: Appointment) -> None:
        data = AppointmentNotifyData.from_appointment(appt)
        user_text = t.NOTIFY_USER_BOOKING_CONFIRMED.format(
            tracking_code=data.tracking_code,
            doctor=data.doctor_name,
            date=format_date_persian(data.schedule_date),
            time=format_time(data.slot_time),
        )
        admin_text = t.NOTIFY_ADMIN_NEW_APPOINTMENT.format(
            tracking_code=data.tracking_code,
            patient_name=data.patient_name,
            phone=data.patient_phone,
            doctor=data.doctor_name,
            date=format_date_persian(data.schedule_date),
            time=format_time(data.slot_time),
        )
        await NotificationService._send_user(bot, data.user_bale_id, user_text)
        await NotificationService._send_all_admins(bot, admin_text)

    @staticmethod
    async def notify_cancellation(bot: "Bot", appt: Appointment, *, by_admin: bool = False) -> None:
        data = AppointmentNotifyData.from_appointment(appt)
        user_text = t.NOTIFY_USER_CANCELLED.format(
            tracking_code=data.tracking_code,
            doctor=data.doctor_name,
            date=format_date_persian(data.schedule_date),
            time=format_time(data.slot_time),
        )
        admin_text = t.NOTIFY_ADMIN_CANCELLED.format(
            tracking_code=data.tracking_code,
            patient_name=data.patient_name,
            doctor=data.doctor_name,
            date=format_date_persian(data.schedule_date),
            time=format_time(data.slot_time),
        )
        if not by_admin:
            await NotificationService._send_user(bot, data.user_bale_id, user_text)
        await NotificationService._send_all_admins(bot, admin_text)

    @staticmethod
    async def send_reminder(
        bot: "Bot",
        appt: Appointment,
        hours_before: int,
    ) -> bool:
        data = AppointmentNotifyData.from_appointment(appt)
        template = t.REMINDER_24H_MESSAGE if hours_before >= 12 else t.REMINDER_2H_MESSAGE
        text = template.format(
            tracking_code=data.tracking_code,
            doctor=data.doctor_name,
            date=format_date_persian(data.schedule_date),
            time=format_time(data.slot_time),
        )
        return await NotificationService._send_user(bot, data.user_bale_id, text)

    @staticmethod
    async def notify_job_summary(bot: "Bot", job_name: str, detail: str) -> None:
        await NotificationService._send_all_admins(bot, f"ℹ️ {job_name}\n\n{detail}")

    @staticmethod
    def appointment_slot_datetime(appt: Appointment) -> datetime:
        return combine_datetime(appt.schedule.schedule_date, appt.slot_time)

    @staticmethod
    def is_in_reminder_window(
        appt: Appointment,
        hours_before: int,
        window_minutes: int,
    ) -> bool:
        slot_dt = NotificationService.appointment_slot_datetime(appt)
        target = now_tz() + timedelta(hours=hours_before)
        window = timedelta(minutes=window_minutes)
        return target - window <= slot_dt <= target + window
