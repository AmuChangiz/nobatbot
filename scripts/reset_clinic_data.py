"""Factory reset — wipe SQLite DB and logs; only .env stays on disk."""
import asyncio
import sys
from pathlib import Path

from app.db.bootstrap import init_database, is_sqlite, sqlite_db_path
from app.db.session import dispose_engine, get_engine


def _clear_logs() -> int:
    log_dir = Path("logs")
    if not log_dir.exists():
        return 0
    removed = 0
    for path in log_dir.glob("*.log*"):
        path.unlink(missing_ok=True)
        removed += 1
    return removed


async def factory_reset() -> tuple[bool, int]:
    if not is_sqlite():
        raise RuntimeError("factory reset فقط برای SQLite پشتیبانی می‌شود")

    db_path = sqlite_db_path()
    db_removed = False
    if db_path is not None:
        for path in (db_path, Path(f"{db_path}-wal"), Path(f"{db_path}-shm")):
            if path.exists():
                path.unlink()
                db_removed = True

    await dispose_engine()
    await init_database(get_engine())

    logs_removed = _clear_logs()
    return db_removed, logs_removed


def main() -> int:
    db_removed, logs_removed = asyncio.run(factory_reset())
    print("پاکسازی کامل انجام شد:\n")
    print(f"  - دیتابیس: {'حذف و ساخته شد از نو' if db_removed else 'ساخته شد از نو'}")
    print(f"  - فایل‌های لاگ: {logs_removed}")
    print("\nفقط .env روی دیسک باقی مانده.")
    print("با start.bat اجرا کن — سوپرادمین از SUPERADMIN_IDS در .env ساخته می‌شود.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"[خطا] {exc}", file=sys.stderr)
        sys.exit(1)
