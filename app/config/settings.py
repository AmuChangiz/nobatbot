from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    bot_token: str = Field(..., alias="BOT_TOKEN")
    database_url: str = Field(..., alias="DATABASE_URL")
    superadmin_ids: list[int] = Field(default_factory=list, alias="SUPERADMIN_IDS")
    slot_lock_ttl_seconds: int = Field(300, alias="SLOT_LOCK_TTL_SECONDS")
    timezone: str = Field("Asia/Tehran", alias="TIMEZONE")

    reminder_24h_hours: int = Field(24, alias="REMINDER_24H_HOURS")
    reminder_2h_hours: int = Field(2, alias="REMINDER_2H_HOURS")
    reminder_window_minutes: int = Field(30, alias="REMINDER_WINDOW_MINUTES")

    daily_report_hour: int = Field(23, alias="DAILY_REPORT_HOUR")
    daily_report_minute: int = Field(59, alias="DAILY_REPORT_MINUTE")

    log_level: str = Field("INFO", alias="LOG_LEVEL")
    log_file: str | None = Field(None, alias="LOG_FILE")
    error_notify_admins: bool = Field(True, alias="ERROR_NOTIFY_ADMINS")

    job_lock_cleanup_interval_minutes: int = Field(1, alias="JOB_LOCK_CLEANUP_INTERVAL_MINUTES")
    job_reminder_interval_minutes: int = Field(15, alias="JOB_REMINDER_INTERVAL_MINUTES")

    @field_validator("superadmin_ids", mode="before")
    @classmethod
    def parse_superadmin_ids(cls, value: str | list[int] | int) -> list[int]:
        if isinstance(value, list):
            return [int(v) for v in value]
        if isinstance(value, int):
            return [value]
        if not value:
            return []
        return [int(part.strip()) for part in str(value).split(",") if part.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
