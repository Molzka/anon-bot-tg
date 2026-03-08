import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from core.config import BOT_TOKEN
from core.database import create_db
from handlers import setup_routers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    create_db()
    bot = Bot(token=BOT_TOKEN)

    dp = Dispatcher(storage=MemoryStorage())

    root_router = setup_routers()
    dp.include_router(root_router)

    logger.info("Бот запускается...")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Бот остановлен.")


if __name__ == "__main__":
    asyncio.run(main())
