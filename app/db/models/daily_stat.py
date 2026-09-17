from datetime import date, datetime

from sqlalchemy import Date, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DailyStatistics(Base):
    __tablename__ = "daily_statistics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stat_date: Mapped[date] = mapped_column(Date, unique=True, nullable=False, index=True)
    total_users: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    new_users: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_appointments: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    new_appointments: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    confirmed_appointments: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cancelled_appointments: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    completed_appointments: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active_doctors: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active_specialties: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
