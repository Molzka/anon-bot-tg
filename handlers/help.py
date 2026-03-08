from aiogram import Bot, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command

from core.config import ADMIN_ID
from crud import db_get_or_create_user

router = Router()


@router.message(Command("help"))
async def cmd_help(message: types.Message):
    text = (
        "📋 <b>Команды</b>\n\n"
        "/start — получить ссылку\n"
        "/mylink — показать ссылку повторно\n"
        "/cancel — отменить текущее действие\n"
        "/help — справка\n"
    )
    if str(message.from_user.id) == str(ADMIN_ID):
        text += (
            "\n🔧 <b>Админ</b>\n"
            "/debug — вкл / выкл debug-режим\n"
            "/broadcast — рассылка\n"
            "/stats — статистика\n"
        )
    await message.answer(text, parse_mode=ParseMode.HTML)


@router.message(Command("mylink"))
async def cmd_mylink(message: types.Message, bot: Bot):
    user = db_get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name,
    )
    me = await bot.get_me()
    link = f"https://t.me/{me.username}?start={user.unique_code}"
    await message.answer(
        f"🔗 <b>Ваша ссылка:</b>\n<code>{link}</code>",
        parse_mode=ParseMode.HTML,
    )
