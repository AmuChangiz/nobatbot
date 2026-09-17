from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.models.appointment import Appointment
    from app.db.models.schedule import Schedule
    from app.db.models.slot_lock import SlotLock
    from app.db.models.specialty import Specialty


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    specialty_id: Mapped[int] = mapped_column(
        ForeignKey("specialties.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    specialty: Mapped["Specialty"] = relationship("Specialty", back_populates="doctors")
    schedules: Mapped[list["Schedule"]] = relationship(
        "Schedule", back_populates="doctor", lazy="selectin"
    )
    appointments: Mapped[list["Appointment"]] = relationship(
        "Appointment", back_populates="doctor", lazy="selectin"
    )
    slot_locks: Mapped[list["SlotLock"]] = relationship(
        "SlotLock", back_populates="doctor", lazy="selectin"
    )
