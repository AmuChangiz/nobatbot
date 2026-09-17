from app.bot.bale_compat import Router

from app.bot.handlers.admin.address import router as address_router
from app.bot.handlers.admin.admins import router as admins_router
from app.bot.handlers.admin.announcements import router as announcements_router
from app.bot.handlers.admin.appointments import router as appointments_router
from app.bot.handlers.admin.broadcast import router as broadcast_router
from app.bot.handlers.admin.doctor import router as doctor_router
from app.bot.handlers.admin.panel import router as panel_router
from app.bot.handlers.admin.schedule import router as schedule_router
from app.bot.handlers.admin.settings import router as settings_router
from app.bot.handlers.admin.specialty import router as specialty_router
from app.bot.handlers.admin.stats import router as stats_router
from app.bot.handlers.admin.support import router as support_router

admin_router = Router(name="admin")
admin_router.include_router(panel_router)
admin_router.include_router(specialty_router)
admin_router.include_router(doctor_router)
admin_router.include_router(schedule_router)
admin_router.include_router(appointments_router)
admin_router.include_router(announcements_router)
admin_router.include_router(address_router)
admin_router.include_router(support_router)
admin_router.include_router(admins_router)
admin_router.include_router(settings_router)
admin_router.include_router(stats_router)
admin_router.include_router(broadcast_router)
