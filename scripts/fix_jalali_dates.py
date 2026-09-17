"""Fix schedules saved with Jalali year mistaken as Gregorian."""
import sqlite3
from datetime import date
from pathlib import Path

import jdatetime


def fix_misparsed_schedules(db_path: Path) -> int:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    rows = cur.execute("SELECT id, schedule_date FROM schedules").fetchall()
    fixed = 0
    for row_id, schedule_date in rows:
        d = date.fromisoformat(schedule_date)
        if d.year < 2000:
            corrected = jdatetime.date(d.year, d.month, d.day).togregorian()
            cur.execute(
                "UPDATE schedules SET schedule_date = ? WHERE id = ?",
                (corrected.isoformat(), row_id),
            )
            fixed += 1
    conn.commit()
    conn.close()
    return fixed


if __name__ == "__main__":
    count = fix_misparsed_schedules(Path(__file__).resolve().parents[1] / "data" / "clinic.db")
    print(f"Fixed {count} schedule(s)")
