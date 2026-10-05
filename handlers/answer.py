import re

from aiogram import Bot, F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from core.config import QUESTION_COOLDOWN_SECONDS
from crud import db_get_question, db_question_cooldown_remaining, db_save_question
from states import AskState, ReplyState
from utils import DeliveryStatus, deliver, extract_media

router = Router()


def valid_question_id(value) -> bool:
    return type(value) is int and 0 < value <= 9223372036854775807


def delivery_error(status: DeliveryStatus) -> str:
    if status is DeliveryStatus.BLOCKED:
        return (
            "❌ Получатель недоступен: возможно, он заблокировал бота. "
            "Доставка не завершена."
        )
    if status is DeliveryStatus.TEMPORARY_ERROR:
        return (
            "❌ Telegram временно недоступен или ограничил отправку. "
            "Доставку подтвердить не удалось. Попробуйте позже."
        )
    return "❌ Telegram не принял сообщение. Попробуйте другой формат."


@router.callback_query(F.data.startswith("answer"))
async def cb_answer(callback: types.CallbackQuery, state: FSMContext):
    match = re.fullmatch(r"answer:([1-9][0-9]{0,18})", callback.data or "")
    if not match or not valid_question_id(int(match[1])):
        await callback.answer("Некорректная кнопка ответа. Откройте исходный вопрос.", show_alert=True)
        return
    qid = int(match[1])
    question = db_get_question(qid)

    if not question:
        await callback.answer("Кнопка устарела: вопрос больше не найден.", show_alert=True)
        return

    if question.to_user_id != callback.from_user.id:
        await callback.answer("Ответить может только получатель этого вопроса.", show_alert=True)
        return

    if (
        not isinstance(callback.message, types.Message)
        or callback.message.chat.type != "private"
        or callback.message.chat.id != callback.from_user.id
    ):
        await callback.answer("Кнопка недоступна. Откройте вопрос в личном чате с ботом.", show_alert=True)
        return

    await callback.answer()
    await state.set_data({"answer_qid": qid})
    await state.set_state(ReplyState.waiting_for_answer)

    await callback.message.answer(
        "<b>Отправьте ваш ответ</b>\n\nТекст, фото, видео, GIF, документ, "
        "голосовое, аудио, кружочек или стикер.\nОтмена — /cancel",
        parse_mode=ParseMode.HTML,
    )


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

    remaining = db_question_cooldown_remaining(message.from_user.id, QUESTION_COOLDOWN_SECONDS)
    if remaining:
        await message.answer(f"Слишком часто. Отправьте вопрос через {remaining} сек.\nОтмена — /cancel")
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

    header = "Вам отправлен новый вопрос:\n\n"
    result = await deliver(bot, target_id, message, header, reply_markup=kb)
    await state.clear()

    if result is DeliveryStatus.SENT:
        await message.answer("✅ Анонимное сообщение отправлено!")
    else:
        await message.answer(
            delivery_error(result) + "\nЧасть сообщения могла дойти. "
            "Для новой попытки откройте ссылку получателя заново."
        )


@router.message(StateFilter(ReplyState.waiting_for_answer))
async def on_answer(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    qid = data.get("answer_qid")
    question = db_get_question(qid) if valid_question_id(qid) else None

    if not question:
        await state.clear()
        await message.answer("❌ Вопрос больше не доступен. Нажмите «Ответить» у исходного вопроса заново.")
        return

    if question.to_user_id != message.from_user.id:
        await state.clear()
        await message.answer("❌ Ответить может только получатель этого вопроса.")
        return

    msg_type, *_ = extract_media(message)
    if msg_type is None:
        await message.answer("❌ Тип сообщения не поддерживается.")
        return

    header = "Ответ на ваш анонимный вопрос:\n\n"
    result = await deliver(bot, question.from_user_id, message, header)
    await state.clear()

    if result is DeliveryStatus.SENT:
        await message.answer("✅ Ответ отправлен!")
    else:
        await message.answer(
            delivery_error(result) + "\nЧасть ответа могла дойти. "
            "Для новой попытки нажмите «Ответить» заново."
        )


@router.callback_query()
async def cb_obsolete(callback: types.CallbackQuery):
    await callback.answer(
        "Эта кнопка устарела. Откройте исходный вопрос или используйте /start.",
        show_alert=True,
    )
