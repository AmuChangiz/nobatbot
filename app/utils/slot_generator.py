from datetime import date, datetime, time, timedelta

from app.utils.datetime_helpers import combine_datetime, get_tz, now_tz


def generate_slots(
    schedule_date: date,
    start_time: time,
    end_time: time,
    visit_duration_minutes: int,
) -> list[time]:
    if visit_duration_minutes <= 0:
        return []

    start_dt = combine_datetime(schedule_date, start_time)
    end_dt = combine_datetime(schedule_date, end_time)

    if start_dt >= end_dt:
        return []

    slots: list[time] = []
    current = start_dt
    duration = timedelta(minutes=visit_duration_minutes)

    while current + duration <= end_dt:
        slots.append(current.time().replace(tzinfo=None))
        current += duration

    return slots


def is_slot_in_past(schedule_date: date, slot_time: time) -> bool:
    slot_dt = combine_datetime(schedule_date, slot_time)
    return slot_dt <= now_tz()
