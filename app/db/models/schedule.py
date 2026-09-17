from datetime import date, datetime, time
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.appointment import Appointment
    from app.db.models.doctor import Doctor
    from app.db.models.slot_lock import SlotLock


class Schedule(Base):
    __tablename__ = "schedules"
    __table_args__ = (
        UniqueConstraint("doctor_id", "schedule_date", name="uq_doctor_schedule_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    schedule_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    visit_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="schedules")
    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment", back_populates="schedule", lazy="selectin"
    )
    slot_locks: Mapped[list["SlotLock"]] = relationship(
        "SlotLock", back_populates="schedule", lazy="selectin"
    )
