import enum
from datetime import datetime, time

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Time,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AppointmentStatus(str, enum.Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class AppointmentTypeEnum(str, enum.Enum):
    IN_PERSON = "in_person"
    ONLINE = "online"
    FOLLOW_UP = "follow_up"
    FIRST_VISIT = "first_visit"


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        Index(
            "ix_appointments_schedule_slot_active",
            "schedule_id",
            "slot_time",
            unique=True,
            sqlite_where=text("status = 'confirmed'"),
        ),
        Index("ix_appointments_user_status", "user_id", "status"),
        Index("ix_appointments_schedule", "schedule_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    schedule_id: Mapped[int] = mapped_column(
        ForeignKey("schedules.id", ondelete="RESTRICT"), nullable=False
    )
    slot_time: Mapped[time] = mapped_column(Time, nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus, name="appointment_status", native_enum=False),
        default=AppointmentStatus.CONFIRMED,
        nullable=False,
    )
    patient_name: Mapped[str] = mapped_column(String(255), nullable=False)
    patient_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    appointment_type: Mapped[str] = mapped_column(String(32), nullable=False, default="in_person")
    tracking_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    reminder_24h_sent: Mapped[bool] = mapped_column(default=False, nullable=False)
    reminder_2h_sent: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    schedule = relationship("Schedule", back_populates="appointments")
