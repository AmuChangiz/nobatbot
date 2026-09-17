# راه‌اندازی روی Windows Server

**Python + SQLite** — حدود **۸۰ MB RAM**

## پیش‌نیاز

1. **Python 3.12** از [python.org](https://www.python.org/downloads/) — تیک **Add to PATH**
2. فایل **`.env`** با `BOT_TOKEN` و `SUPERADMIN_IDS`

## نصب و اجرا

```
setup.bat    ← یک‌بار
start.bat    ← اجرای ربات
```

| فایل | کار |
|------|-----|
| `setup.bat` | ساخت venv و نصب پکیج‌ها |
| `start.bat` | اجرای ربات |
| `stop.bat` | توقف ربات |
| `restart.bat` | راه‌اندازی مجدد |
| `logs.bat` | مشاهده لاگ زنده |
| `danger/reset.bat` | ⚠️ factory reset — فقط `.env` می‌ماند |

## انتقال به سرور

1. کل پوشه را کپی کنید (شامل `.env` و `data/clinic.db`)
2. Python 3.12 را روی سرور نصب کنید
3. اگر `.venv` نبود: `setup.bat`
4. `start.bat`

> **نکته:** `.venv` را لازم نیست از PC دیگر کپی کنید — روی سرور با `setup.bat` ساخته می‌شود.

## اجرای خودکار

Task Scheduler → At startup → Action:

```
C:\path\to\bot\start.bat
```

## تست

1. در بله: `/start`
2. پنل ادمین: `/admin`

## عیب‌یابی

**ربات پاسخ نمی‌دهد:** `logs.bat` یا فایل `logs/bot.log`

**چند instance:** فقط یک‌بار `start.bat` بزنید — خودش instance قبلی را می‌بندد.
