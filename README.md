# Clinic Appointment Bot (Bale)

**English** | [فارسی](README.fa.md)

A [Bale](https://ble.ir) messenger bot for clinic appointment booking. Patients pick a specialty, doctor, date, and time. Admins define doctor schedules and manage bookings.

Bot messages and menus are **Persian**. Dates in the UI use the **Jalali** calendar. The default database is **SQLite**, and the bot runs on Windows at about **80 MB RAM**.

## Contents

- [Features](#features)
- [Requirements](#requirements)
- [Install and run](#install-and-run)
- [Configuration](#configuration)
- [How it works](#how-it-works)
- [Patient booking flow](#patient-booking-flow)
- [Admin panel](#admin-panel)
- [Roles and permissions](#roles-and-permissions)
- [Data model](#data-model)
- [Background jobs](#background-jobs)
- [Project layout](#project-layout)
- [Scripts](#scripts)
- [Security](#security)
- [Troubleshooting](#troubleshooting)

## Features

### Patients

- Main menu: new appointment, my appointments, address, support
- Multi-step booking with inline keyboards and back navigation
- Resume an unfinished booking or start over
- Temporary slot lock while the user finishes booking (default 5 minutes)
- Unique tracking code: `CLN-YYMMDD-XXXXX`
- View and cancel active appointments
- Automatic reminders about 24 hours and 2 hours before the visit
- Clinic address and support text (editable in the admin panel)
- Active announcements shown under support

### Admins

- Panel via `/admin`
- Manage specialties, doctors, and daily schedules (start/end time and visit duration)
- Search bookings by tracking code, name, or phone
- Set status: confirmed, cancelled, completed, no-show
- Announcements, address, support
- System stats and a daily report for admins
- Broadcast to all registered users
- Admin management (superadmin only)

## Requirements

- **Python 3.12** (or 3.13); on Windows, check **Add to PATH**
- A bot account on the [Bale platform](https://ble.ir) and a **bot token**
- Numeric Bale user IDs for superadmins (`SUPERADMIN_IDS`)

You can usually get a user ID from Bale or from the log after the first `/start`.

## Install and run

### Windows (recommended)

```text
setup.bat     once: create venv, install packages, copy .env if missing
start.bat     run the bot (stops a previous instance first)
stop.bat      stop
restart.bat   restart
logs.bat      live log
```

If `.env` is missing, `setup.bat` copies `.env.example` and stops so you can set `BOT_TOKEN` and `SUPERADMIN_IDS`. Run `setup.bat` again, then `start.bat`.

Windows Server notes: [WINDOWS_SERVER.md](WINDOWS_SERVER.md) · [فارسی](WINDOWS_SERVER.fa.md)

### Manual (any OS)

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # or: cp .env.example .env
# edit .env
python bale_bot.py
```

Entry point is `bale_bot.py`. The bot uses **polling** against the Bale API.

## Configuration

Settings are loaded from `.env` (`Settings` in `app/config/settings.py`).

| Variable | Meaning | Default |
|----------|---------|---------|
| `BOT_TOKEN` | Bale bot token | required |
| `SUPERADMIN_IDS` | Superadmin Bale IDs, comma-separated | required for `/admin` |
| `DATABASE_URL` | Database URL | `sqlite+aiosqlite:///./data/clinic.db` |
| `TIMEZONE` | Time zone | `Asia/Tehran` |
| `SLOT_LOCK_TTL_SECONDS` | Slot lock TTL while booking | `300` |
| `REMINDER_24H_HOURS` | First reminder offset | `24` |
| `REMINDER_2H_HOURS` | Second reminder offset | `2` |
| `REMINDER_WINDOW_MINUTES` | Reminder send window | `30` |
| `JOB_REMINDER_INTERVAL_MINUTES` | How often reminders are checked | `15` |
| `JOB_LOCK_CLEANUP_INTERVAL_MINUTES` | How often expired locks are cleaned | `1` |
| `DAILY_REPORT_HOUR` / `DAILY_REPORT_MINUTE` | Daily report time | `23` / `59` |
| `LOG_LEVEL` | Log level | `INFO` |
| `LOG_FILE` | Log file path | `logs/bot.log` |
| `ERROR_NOTIFY_ADMINS` | Notify superadmins on errors | `true` |

SQLite creates tables on startup (`create_all`). Non-SQLite databases are not auto-bootstrapped in the current code.

## How it works

```text
Bale (polling)
    → BaleApplication  (compat layer over python-bale-bot)
        → Router  (admin, then user)
            → Handler + FSM (MemoryStorage)
                → SQLAlchemy AsyncSession
                    → services (booking, slots, notifications, stats, …)
                        → SQLite: data/clinic.db

APScheduler (alongside the bot)
    → reminders, daily report, lock and past-schedule cleanup
```

`app/bot/bale_compat` exposes an aiogram-style API (Router, `F` filters, FSM, handlers) on top of the official Bale SDK.

On each message or callback:

1. The user is created or updated in `users`.
2. Admin status is resolved for that request.
3. A DB session is opened and committed after the handler.
4. Handler errors are logged and, if enabled, sent to superadmins.

FSM lives in memory: a process restart drops an unfinished booking. Slot locks stay in the database until TTL expires.

## Patient booking flow

`/start` shows the main menu. If a booking is in progress, the user can resume or start over.

Steps (`BookingStates`):

1. **Specialty** — active specialties only
2. **Doctor** — active doctors in that specialty with at least one free slot
3. **Date** — days that still have free slots (Jalali in the UI)
4. **Time** — slots generated from that day’s schedule
5. **Phone** — contact share or manual `09xxxxxxxxx`
6. **Patient name**
7. **Confirm** — save the appointment, issue a tracking code, release the lock

Slots are generated from `start_time` to `end_time` in steps of `visit_duration_minutes`. Past, already confirmed, or locked slots are hidden.

### Concurrent booking

When the user picks a time, a `slot_locks` row is stored with `locked_until`. Until TTL expires, others cannot take that slot. A SQLite unique index on `(schedule_id, slot_time)` for `confirmed` rows blocks two active bookings on the same slot. Cancel, main menu, or a new booking releases the user’s lock.

Each doctor has at most **one schedule per date** (`uq_doctor_schedule_date`).

## Admin panel

Command: `/admin` — active rows in `admins` only.

| Section | What it does |
|---------|----------------|
| Specialties | Add, edit, toggle, delete (deactivates if doctors exist) |
| Doctors | Add with specialty and bio, toggle active |
| Schedules | Date (Jalali or Gregorian), start/end, visit duration, slot count |
| Appointments | Search, recent list, cancel, completed, no-show |
| Announcements | Title and body; shown in patient support |
| Address / support | Free text for the patient menu |
| Settings | Values from `.env` (edit the file) |
| Stats | Users, admins, specialties, doctors, bookings, today’s visits |
| Broadcast | Send to all `bale_user_id`s, pause every 25 messages |
| Admins | Add by Bale ID, promote/demote superadmin (superadmin only) |

After first run:

1. `/admin` with a superadmin account
2. Add at least one specialty
3. Add a doctor
4. Add a schedule on a future date
5. Test booking with `/start`

## Roles and permissions

| Role | Source | Access |
|------|--------|--------|
| Superadmin | Bootstrapped from `SUPERADMIN_IDS`; can be promoted in the panel | Everything, including admin management |
| Admin | Added in the panel | Everything except admin management |
| User | Anyone who starts the bot | Own bookings only |

A superadmin cannot be removed from the panel.

Appointment statuses (`AppointmentStatus`): `confirmed`, `cancelled`, `completed`, `no_show`.

## Data model

Database file: `data/clinic.db`

| Table | Contents |
|-------|----------|
| `users` | Bale user (id, name, username, phone) |
| `admins` | Admin and superadmin flag |
| `specialties` | Specialty |
| `doctors` | Doctor under a specialty |
| `schedules` | One day’s schedule for a doctor |
| `appointments` | Visit + tracking code + reminder flags |
| `slot_locks` | Temporary slot lock |
| `bot_settings` | Key/value (address, support) |
| `announcements` | Announcement |
| `broadcast_messages` | Broadcast history |
| `daily_statistics` | Stored daily stats |

Main chain: specialty → doctor → schedule → appointment. Appointments also link to user and doctor.

## Background jobs

APScheduler uses the timezone from `.env`.

| Job id | When | What |
|--------|------|------|
| `cleanup_locks` | every 1 minute (configurable) | Delete expired locks |
| `cleanup_nightly` | 03:00 | Stale locks + past schedules with no bookings |
| `reminder_24h` / `reminder_2h` | every 15 minutes | Send reminders in the time window |
| `daily_report` | 23:59 (configurable) | Daily report to admins |
| `generate_statistics` | same as the report | Persist daily stats |

On startup, past-day schedules with no appointments are removed.

## Project layout

```text
bale_bot.py              entry: database, superadmins, scheduler, polling
app/
  config/                settings from .env
  core/                  logging and error reports to superadmins
  db/                    models, session, SQLite bootstrap
  services/              booking, slots, notifications, stats, …
  bot/
    bale_compat/         Router, FSM, filters, Application on the Bale SDK
    handlers/user/       start, menu, booking, my appointments
    handlers/admin/      admin panel
    keyboards/           reply and inline keyboards
    states/              FSM
    texts/fa.py          all Persian copy
    permissions.py       roles and Permission
  scheduler/             jobs and broadcast
  utils/                 Jalali dates, slots, tracking codes, phone validation
scripts/                 maintenance tools
danger/                  factory reset (destructive)
```

Main dependencies (`requirements.txt`): `python-bale-bot`, SQLAlchemy asyncio, aiosqlite, APScheduler, pydantic-settings, jdatetime, pytz.

## Scripts

| Path | Purpose |
|------|---------|
| `scripts/check_db.py` | Inspect the database |
| `scripts/fix_jalali_dates.py` | Fix Jalali dates in stored data |
| `scripts/test_rebook.py` | Rebook scenario test |
| `scripts/reset_clinic_data.py` | Wipe SQLite DB and logs; keep `.env` |
| `danger/reset.bat` | Same reset with typed `RESET` confirm — [danger/README.md](danger/README.md) |

Reset is SQLite-only. Afterward, define specialty, doctor, and schedule again.

## Security

These paths are in `.gitignore` and must not be committed:

- `.env` (bot token)
- `data/` (patient database)
- `logs/`
- `.venv/`

Keep `.env.example` in the repo; put the real `.env` only on the server. Do not paste tokens into issues or screenshots. If a token leaks, rotate it in the Bale bot panel.

Back up `data/clinic.db` on the server separately.

## Troubleshooting

**Bot does not reply.** Check `logs/bot.log` or `logs.bat`. Verify token and server network. Run only one instance; `start.bat` kills a previous `bale_bot.py`.

**`/admin` does nothing.** The Bale ID must match `SUPERADMIN_IDS`. Restart after editing `.env` so superadmin bootstrap runs.

**No free slots.** That doctor needs a future schedule, and slots must not be full or locked.

**Wrong dates.** Use `TIMEZONE=Asia/Tehran`. The panel accepts Jalali (`1404/06/20`) or Gregorian (`2025-09-11`).

**FSM memory.** Restarting mid-booking clears the step; the user must book again from the menu.

## License

This repository is intended for clinic use and deployment. Add a `LICENSE` file if you want an explicit open-source license.
