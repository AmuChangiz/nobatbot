# Deploy on Windows Server

**English** | [فارسی](WINDOWS_SERVER.fa.md)

**Python + SQLite** — about **80 MB RAM**

## Requirements

1. **Python 3.12** from [python.org](https://www.python.org/downloads/) — check **Add to PATH**
2. A **`.env`** file with `BOT_TOKEN` and `SUPERADMIN_IDS`

## Install and run

```
setup.bat    ← once
start.bat    ← run the bot
```

| File | Purpose |
|------|---------|
| `setup.bat` | Create venv and install packages |
| `start.bat` | Run the bot |
| `stop.bat` | Stop the bot |
| `restart.bat` | Restart |
| `logs.bat` | Live log |
| `danger/reset.bat` | ⚠️ factory reset — only `.env` stays on disk |

## Move to a server

1. Copy the whole folder (including `.env` and `data/clinic.db`)
2. Install Python 3.12 on the server
3. If `.venv` is missing: `setup.bat`
4. `start.bat`

> **Note:** You do not need to copy `.venv` from another PC — create it on the server with `setup.bat`.

## Run at startup

Task Scheduler → At startup → Action:

```
C:\path\to\bot\start.bat
```

## Test

1. In Bale: `/start`
2. Admin panel: `/admin`

## Troubleshooting

**Bot does not reply:** `logs.bat` or `logs/bot.log`

**Multiple instances:** run `start.bat` only once — it stops the previous process.
