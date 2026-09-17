from app.bot.bale_compat import Router

from app.bot.handlers.user.appointments import router as appointments_router
from app.bot.handlers.user.booking import router as booking_router
from app.bot.handlers.user.errors import router as errors_router
from app.bot.handlers.user.menu import router as menu_router
from app.bot.handlers.user.start import router as start_router

user_router = Router(name="user")
user_router.include_router(errors_router)
user_router.include_router(start_router)
user_router.include_router(menu_router)
user_router.include_router(booking_router)
user_router.include_router(appointments_router)
