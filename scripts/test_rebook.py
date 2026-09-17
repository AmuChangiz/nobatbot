"""Test rebooking a cancelled slot after index migration."""
import asyncio

from sqlalchemy import select, text

from app.db.bootstrap import init_database
from app.db.models import Appointment, AppointmentStatus
from app.db.session import get_engine, get_session_factory
from app.services import AppointmentService


async def main() -> None:
    engine = get_engine()
    await init_database(engine)

    async with engine.connect() as conn:
        rows = await conn.execute(text("PRAGMA index_list('appointments')"))
        print("indexes:", [row[1] for row in rows.fetchall()])

    session_factory = get_session_factory()
    async with session_factory() as session:
        cancelled = (
            await session.execute(
                select(Appointment).where(Appointment.status == AppointmentStatus.CANCELLED)
            )
        ).scalars().first()
        if not cancelled:
            print("no cancelled appointment in db")
            return

        appt = await AppointmentService.book(
            session,
            cancelled.user_id,
            cancelled.schedule_id,
            cancelled.slot_time,
            "Test",
            "09128893996",
        )
        print("rebook ok:", appt.tracking_code if appt else "FAILED")
        await session.rollback()


if __name__ == "__main__":
    asyncio.run(main())
