from datetime import datetime, time

from sqlalchemy import DateTime, ForeignKey, Index, Integer, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SlotLock(Base):
    __tablename__ = "slot_locks"
    __table_args__ = (
        Index("ix_slot_locks_schedule_slot", "schedule_id", "slot_time", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    schedule_id: Mapped[int] = mapped_column(
        ForeignKey("schedules.id", ondelete="CASCADE"), nullable=False
    )
    slot_time: Mapped[time] = mapped_column(Time, nullable=False)
    locked_until: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user = relationship("User", back_populates="slot_locks")
    doctor = relationship("Doctor", back_populates="slot_locks")
    schedule = relationship("Schedule", back_populates="slot_locks")
