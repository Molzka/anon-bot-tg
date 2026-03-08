from aiogram import Bot, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from crud import db_get_or_create_user, db_user_by_code
from states import AskState

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext, bot: Bot):
    await state.clear()

    user = db_get_or_create_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name,
    )

    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        code = parts[1].strip()
        target = db_user_by_code(code)

        if not target:
            await message.answer("❌ Ссылка недействительна.")
            return

        if str(target.user_id) == str(message.from_user.id):
            await message.answer(
                "Вы не можете отправить анонимный вопрос самому себе!\n"
                "Поделитесь ссылкой с другими."
            )
            return

        await state.update_data(target_user_id=target.user_id)
        await state.set_state(AskState.waiting_for_question)
        await message.answer(
            "✉️ <b>Напишите анонимное сообщение</b>\n\n"
            "Поддерживаются: текст, фото, видео, голосовое, "
            "кружочек, документ, стикер, аудио, GIF.\n\n"
            "Отмена — /cancel",
            parse_mode=ParseMode.HTML,
        )
        return

    me = await bot.get_me()
    link = f"https://t.me/{me.username}?start={user.unique_code}"

    await message.answer(
        f"<b>Добро пожаловать!</b>\n\n"
        f"Это бот анонимных вопросов.\n\n"
        f"🔗 <b>Ваша персональная ссылка:</b>\n"
        f"<code>{link}</code>\n\n"
        f"Отправьте её друзьям — они смогут задать "
        f"вам вопрос анонимно!\n\n"
        f"Все команды — /help",
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    current = await state.get_state()
    if current is None:
        await message.answer("Нечего отменять.")
        return
    await state.clear()
    await message.answer("❌ Действие отменено.")
