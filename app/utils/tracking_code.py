import secrets

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Appointment
from app.utils import today_local


async def generate_tracking_code(session: AsyncSession) -> str:
    date_part = today_local().strftime("%y%m%d")
    for _ in range(20):
        suffix = secrets.token_hex(3).upper()[:5]
        code = f"CLN-{date_part}-{suffix}"
        exists = await session.scalar(
            select(Appointment.id).where(Appointment.tracking_code == code)
        )
        if exists is None:
            return code
    raise RuntimeError("Unable to generate unique tracking code")
