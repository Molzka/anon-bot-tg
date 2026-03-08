from aiogram import Bot, F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from crud import db_get_question, db_save_question
from states import AskState, ReplyState
from utils import deliver, extract_media, notify_debug

router = Router()


@router.callback_query(F.data.startswith("answer:"))
async def cb_answer(callback: types.CallbackQuery, state: FSMContext):
    qid = int(callback.data.split(":")[1])
    question = db_get_question(qid)

    if not question:
        await callback.answer("Вопрос не найден.", show_alert=True)
        return

    await state.update_data(
        answer_to_user=question.from_user_id,
        answer_qid=qid,
    )
    await state.set_state(ReplyState.waiting_for_answer)

    await callback.message.answer(
        "<b>Отправьте ваш ответ</b>\n\nПоддерживаются любые форматы.\nОтмена — /cancel",
        parse_mode=ParseMode.HTML,
    )
    await callback.answer()


@router.message(StateFilter(AskState.waiting_for_question))
async def on_question(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    target_id = data.get("target_user_id")

    if not target_id:
        await state.clear()
        await message.answer("❌ Ошибка. Перейдите по ссылке заново.")
        return

    msg_type, content, file_id, caption = extract_media(message)
    if msg_type is None:
        await message.answer("❌ Тип сообщения не поддерживается. Попробуйте другой.")
        return

    q = db_save_question(
        from_id=message.from_user.id,
        to_id=target_id,
        msg_type=msg_type,
        content=content,
        file_id=file_id,
        caption=caption,
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Ответить", callback_data=f"answer:{q.id}")]
        ]
    )

    header = "<i>Вам отправлен новый вопрос:</i>\n\n"
    ok = await deliver(bot, target_id, message, header, reply_markup=kb)

    if ok:
        await message.answer("✅ Анонимное сообщение отправлено!")
        await notify_debug(bot, message.from_user, target_id, "ВОПРОС", message)
    else:
        await message.answer(
            "❌ Не удалось доставить сообщение.\n"
            "Возможно, получатель заблокировал бота."
        )

    await state.clear()


@router.message(StateFilter(ReplyState.waiting_for_answer))
async def on_answer(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    to_id = data.get("answer_to_user")

    if not to_id:
        await state.clear()
        await message.answer("❌ Ошибка. Нажмите «Ответить» заново.")
        return

    msg_type, *_ = extract_media(message)
    if msg_type is None:
        await message.answer("❌ Тип сообщения не поддерживается.")
        return

    header = "<i>Ответ на ваш анонимный вопрос:</i>\n\n"
    ok = await deliver(bot, to_id, message, header)

    if ok:
        await message.answer("✅ Ответ отправлен!")
        await notify_debug(bot, message.from_user, to_id, "ОТВЕТ", message)
    else:
        await message.answer(
            "❌ Не удалось доставить ответ.\nВозможно, пользователь заблокировал бота."
        )

    await state.clear()
