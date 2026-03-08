from aiogram import Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from core.config import ADMIN_ID
from crud import (
    db_count_questions,
    db_count_users,
    db_debug_enabled,
    db_toggle_debug,
)
from states import BroadcastState

router = Router()


@router.message(Command("debug"))
async def cmd_debug(message: types.Message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    print(ADMIN_ID)
    state = db_toggle_debug()
    print(state)
    await message.answer(f"Debug-режим: {'включён' if state else 'выключен'}")


@router.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message, state: FSMContext):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    await state.set_state(BroadcastState.waiting_for_message)
    await message.answer(
        "Отправьте сообщение для рассылки (любой формат).\nОтмена — /cancel"
    )


@router.message(Command("stats"))
async def cmd_stats(message: types.Message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    await message.answer(
        f"<b>Статистика</b>\n\n"
        f"Пользователей: {db_count_users()}\n"
        f"Вопросов: {db_count_questions()}\n"
        f"Debug: {'✅' if db_debug_enabled() else '❌'}",
        parse_mode=ParseMode.HTML,
    )
