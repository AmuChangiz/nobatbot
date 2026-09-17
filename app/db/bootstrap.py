from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.config import get_settings
from app.db.base import Base
from app.db.models import *  # noqa: F401, F403


def is_sqlite() -> bool:
    return get_settings().database_url.startswith("sqlite")


def sqlite_db_path() -> Path | None:
    if not is_sqlite():
        return None
    url = get_settings().database_url
    # sqlite+aiosqlite:///./data/clinic.db
    raw = url.split("///", 1)[-1]
    return Path(raw).resolve()


def _migrate_sqlite_appointment_index(connection) -> None:
    rows = connection.execute(text("PRAGMA index_list('appointments')")).fetchall()
    index_names = {row[1] for row in rows}
    if "ix_appointments_schedule_slot" in index_names:
        connection.execute(text("DROP INDEX ix_appointments_schedule_slot"))
    connection.execute(
        text(
            "CREATE UNIQUE INDEX IF NOT EXISTS ix_appointments_schedule_slot_active "
            "ON appointments (schedule_id, slot_time) WHERE status = 'confirmed'"
        )
    )


async def init_database(engine: AsyncEngine) -> None:
    if not is_sqlite():
        return

    db_path = sqlite_db_path()
    if db_path is not None:
        db_path.parent.mkdir(parents=True, exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_migrate_sqlite_appointment_index)
