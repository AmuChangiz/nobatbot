import logging
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Appointment,
    AppointmentStatus,
    DailyStatistics,
    Doctor,
    Specialty,
    User,
)
from app.utils import day_bounds_db, now_db, today_local

logger = logging.getLogger(__name__)


class StatisticsService:
    @staticmethod
    async def generate_daily_snapshot(session: AsyncSession, stat_date: date | None = None) -> DailyStatistics:
        if stat_date is None:
            stat_date = today_local()

        stats = await StatisticsService._collect_stats(session, stat_date)
        generated_at = now_db()

        result = await session.execute(
            select(DailyStatistics).where(DailyStatistics.stat_date == stat_date)
        )
        snapshot = result.scalar_one_or_none()
        if snapshot is None:
            snapshot = DailyStatistics(stat_date=stat_date, **stats, generated_at=generated_at)
            session.add(snapshot)
        else:
            for key, value in stats.items():
                setattr(snapshot, key, value)
            snapshot.generated_at = generated_at

        await session.flush()
        logger.info("Daily statistics generated for %s", stat_date)
        return snapshot

    @staticmethod
    async def _collect_stats(session: AsyncSession, stat_date: date) -> dict:
        start, end = day_bounds_db(stat_date)

        total_users = await session.scalar(select(func.count(User.id))) or 0
        new_users = await session.scalar(
            select(func.count(User.id)).where(User.created_at >= start, User.created_at <= end)
        ) or 0
        total_appointments = await session.scalar(select(func.count(Appointment.id))) or 0
        new_appointments = await session.scalar(
            select(func.count(Appointment.id)).where(
                Appointment.created_at >= start, Appointment.created_at <= end
            )
        ) or 0
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
        active_doctors = await session.scalar(
            select(func.count(Doctor.id)).where(Doctor.is_active.is_(True))
        ) or 0
        active_specialties = await session.scalar(
            select(func.count(Specialty.id)).where(Specialty.is_active.is_(True))
        ) or 0

        return {
            "total_users": total_users,
            "new_users": new_users,
            "total_appointments": total_appointments,
            "new_appointments": new_appointments,
            "confirmed_appointments": confirmed,
            "cancelled_appointments": cancelled,
            "completed_appointments": completed,
            "active_doctors": active_doctors,
            "active_specialties": active_specialties,
        }

    @staticmethod
    async def get_snapshot(session: AsyncSession, stat_date: date) -> DailyStatistics | None:
        result = await session.execute(
            select(DailyStatistics).where(DailyStatistics.stat_date == stat_date)
        )
        return result.scalar_one_or_none()
