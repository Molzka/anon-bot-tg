from aiogram import F, Router

from .admin import router as r_admin
from .answer import router as r_answer
from .help import router as r_help
from .mailing import router as r_mailing
from .start import router as r_start


def setup_routers() -> Router:
    root = Router()
    root.message.filter(F.chat.type == "private")
    root.include_router(r_start)
    root.include_router(r_admin)
    root.include_router(r_help)
    root.include_router(r_answer)
    root.include_router(r_mailing)
    return root
