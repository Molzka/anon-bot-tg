import asyncio

from aiogram import Bot, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext

from core.config import ADMIN_ID
from crud import db_all_users
from states import BroadcastState
from utils import DeliveryStatus, forward_broadcast

router = Router()


@router.message(StateFilter(BroadcastState.waiting_for_message))
async def on_broadcast(message: types.Message, state: FSMContext, bot: Bot):
    if str(message.from_user.id) != str(ADMIN_ID):
        await state.clear()
        return

    users = db_all_users()
    total = len(users)
    ok_count = 0
    fail_count = 0

    status = await message.answer(f"📢 Рассылка… 0 / {total}")

    for i, u in enumerate(users, 1):
        try:
            result = await forward_broadcast(bot, u.user_id, message)
            if result is DeliveryStatus.SENT:
                ok_count += 1
            else:
                fail_count += 1
        except Exception:
            fail_count += 1

        if i % 25 == 0:
            try:
                await status.edit_text(f"📢 Рассылка... {i} / {total}")
            except Exception:
                pass

        await asyncio.sleep(0.05)

    await status.edit_text(
        f"📢 <b>Рассылка завершена</b>\n\n"
        f"✅ Доставлено: {ok_count}\n"
        f"❌ Ошибок: {fail_count}\n"
        f"📊 Всего: {total}",
        parse_mode=ParseMode.HTML,
    )
    await state.clear()
