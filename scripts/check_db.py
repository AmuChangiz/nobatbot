"""Quick DB health check for clinic bot."""
import asyncio
from datetime import date

from app.db.session import get_session_factory
from app.services import DoctorService, ScheduleService, SpecialtyService


async def main() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        specs = await SpecialtyService(session).list_all()
        docs = await DoctorService(session).list_all()
        print(f"تخصص‌ها: {len(specs)}")
        print(f"پزشکان: {len(docs)}")
        for d in docs:
            schedules = await ScheduleService(session).list_by_doctor(d.id)
            future = [s for s in schedules if s.schedule_date >= date.today()]
            print(f"  {d.full_name}: {len(future)} برنامه آینده")
            for s in future[:5]:
                slots = await ScheduleService(session).get_available_slots(s.id)
                print(f"    {s.schedule_date} -> {len(slots)} اسلات")


if __name__ == "__main__":
    asyncio.run(main())
