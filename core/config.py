import os
from pathlib import Path
import re

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def positive_int(name: str, default: str = "") -> int:
    try:
        value = int(os.getenv(name, default))
    except ValueError:
        raise ValueError(f"{name}: укажите положительное целое число в .env") from None
    if value <= 0:
        raise ValueError(f"{name}: укажите положительное целое число в .env")
    return value


BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
if not re.fullmatch(r"[0-9]+:[A-Za-z0-9_-]+", BOT_TOKEN):
    raise ValueError("BOT_TOKEN: укажите токен бота из @BotFather в .env")

ADMIN_ID = positive_int("ADMIN_ID")
QUESTION_COOLDOWN_SECONDS = positive_int("QUESTION_COOLDOWN_SECONDS", "30")
DATABASE_PATH = PROJECT_ROOT / "bot.db"
