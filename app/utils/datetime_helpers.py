from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import jdatetime

from app.config import get_settings

_JALALI_WEEKDAYS = [
    "شنبه",
    "یکشنبه",
    "دوشنبه",
    "سه‌شنبه",
    "چهارشنبه",
    "پنجشنبه",
    "جمعه",
]


def get_tz() -> ZoneInfo:
    return ZoneInfo(get_settings().timezone)


def now_tz() -> datetime:
    return datetime.now(tz=get_tz())


def _uses_sqlite() -> bool:
    return get_settings().database_url.startswith("sqlite")


def now_db() -> datetime:
    """Datetime for DB columns — naive local on SQLite, timezone-aware otherwise."""
    local = now_tz()
    if _uses_sqlite():
        return local.replace(tzinfo=None)
    return local


def day_bounds_db(d: date) -> tuple[datetime, datetime]:
    """Start/end of a calendar day for DB range filters."""
    if _uses_sqlite():
        return datetime.combine(d, time.min), datetime.combine(d, time.max)
    tz = get_tz()
    return (
        datetime.combine(d, time.min, tzinfo=tz),
        datetime.combine(d, time.max, tzinfo=tz),
    )


def today_local() -> date:
    return now_tz().date()


def combine_datetime(schedule_date: date, slot_time: time) -> datetime:
    return datetime.combine(schedule_date, slot_time, tzinfo=get_tz())


def format_date_persian(d: date) -> str:
    jd = jdatetime.date.fromgregorian(date=d)
    weekday = _JALALI_WEEKDAYS[jd.weekday()]
    return f"{weekday} {jd.year}/{jd.month:02d}/{jd.day:02d}"


def format_time(t: time) -> str:
    return t.strftime("%H:%M")


def parse_time(value: str) -> time | None:
    value = value.strip()
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt).time()
        except ValueError:
            continue
    return None


def parse_date(value: str) -> date | None:
    value = value.strip().replace("-", "/")
    parts = value.split("/")
    if len(parts) == 3:
        try:
            y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
            if 1300 <= y <= 1500:
                return jdatetime.date(y, m, d).togregorian()
        except (ValueError, OverflowError):
            pass

    normalized = value.replace("/", "-")
    for fmt in ("%Y-%m-%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(normalized if fmt == "%Y-%m-%d" else value, fmt).date()
        except ValueError:
            continue
    return None


def is_valid_phone(phone: str) -> bool:
    digits = phone.strip().replace(" ", "").replace("-", "")
    if digits.startswith("+98"):
        digits = "0" + digits[3:]
    if digits.startswith("98") and len(digits) == 12:
        digits = "0" + digits[2:]
    return digits.startswith("09") and len(digits) == 11 and digits.isdigit()


def normalize_phone(phone: str) -> str:
    digits = phone.strip().replace(" ", "").replace("-", "")
    if digits.startswith("+98"):
        digits = "0" + digits[3:]
    if digits.startswith("98") and len(digits) == 12:
        digits = "0" + digits[2:]
    return digits
