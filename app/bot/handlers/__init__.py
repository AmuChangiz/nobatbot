from app.bot.bale_compat import Router

from app.bot.handlers.admin import admin_router
from app.bot.handlers.user import user_router


def setup_routers() -> Router:
    root = Router()
    root.include_router(admin_router)
    root.include_router(user_router)
    return root
