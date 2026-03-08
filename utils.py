import logging
from html import escape

from aiogram import Bot, types
from aiogram.enums import ParseMode

from core.config import ADMIN_ID
from crud import db_debug_enabled

logger = logging.getLogger(__name__)


def extract_media(msg: types.Message):
    if msg.text:
        return "text", msg.text, None, None
    if msg.photo:
        return "photo", None, msg.photo[-1].file_id, msg.caption
    if msg.video:
        return "video", None, msg.video.file_id, msg.caption
    if msg.animation:
        return "animation", None, msg.animation.file_id, msg.caption
    if msg.document:
        return "document", None, msg.document.file_id, msg.caption
    if msg.voice:
        return "voice", None, msg.voice.file_id, msg.caption
    if msg.audio:
        return "audio", None, msg.audio.file_id, msg.caption
    if msg.video_note:
        return "video_note", None, msg.video_note.file_id, None
    if msg.sticker:
        return "sticker", None, msg.sticker.file_id, None
    return None, None, None, None


async def deliver(
    bot: Bot,
    chat_id: int,
    msg: types.Message,
    header: str,
    reply_markup=None,
) -> bool:
    try:
        if msg.text:
            await bot.send_message(
                chat_id,
                f"{header}<i>{escape(msg.text)}</i>",
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
            )

        elif msg.photo:
            cap = header + (f"<i>{escape(msg.caption)}</i>" if msg.caption else "")
            await bot.send_photo(
                chat_id,
                photo=msg.photo[-1].file_id,
                caption=cap,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
            )

        elif msg.video:
            cap = header + (f"<i>{escape(msg.caption)}</i>" if msg.caption else "")
            await bot.send_video(
                chat_id,
                video=msg.video.file_id,
                caption=cap,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
            )

        elif msg.animation:
            cap = header + (f"<i>{escape(msg.caption)}</i>" if msg.caption else "")
            await bot.send_animation(
                chat_id,
                animation=msg.animation.file_id,
                caption=cap,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
            )

        elif msg.document:
            cap = header + (f"<i>{escape(msg.caption)}</i>" if msg.caption else "")
            await bot.send_document(
                chat_id,
                document=msg.document.file_id,
                caption=cap,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
            )

        elif msg.voice:
            cap = header + (f"<i>{escape(msg.caption)}</i>" if msg.caption else "")
            await bot.send_voice(
                chat_id,
                voice=msg.voice.file_id,
                caption=cap,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
            )

        elif msg.audio:
            cap = header + (f"<i>{escape(msg.caption)}</i>" if msg.caption else "")
            await bot.send_audio(
                chat_id,
                audio=msg.audio.file_id,
                caption=cap,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup,
            )

        elif msg.video_note:
            await bot.send_message(chat_id, header, parse_mode=ParseMode.HTML)
            await bot.send_video_note(
                chat_id,
                video_note=msg.video_note.file_id,
                reply_markup=reply_markup,
            )

        elif msg.sticker:
            await bot.send_message(chat_id, header, parse_mode=ParseMode.HTML)
            await bot.send_sticker(
                chat_id,
                sticker=msg.sticker.file_id,
                reply_markup=reply_markup,
            )

        else:
            return False

        return True

    except Exception as e:
        logger.error("deliver → %s: %s", chat_id, e)
        return False


async def notify_debug(
    bot: Bot,
    from_user: types.User,
    to_id: int,
    action: str,
    msg: types.Message,
):
    if not db_debug_enabled():
        return
    name = (
        f"@{from_user.username}" if from_user.username else escape(from_user.full_name)
    )
    text = (
        f"<b>{action}</b>\n"
        f"От: {name} (<code>{from_user.id}</code>)\n"
        f"Кому: <code>{to_id}</code>\n"
    )

    m_type, content, _, caption = extract_media(msg)
    text += f"Тип: {m_type}\n"
    if content:
        text += f"Текст: {escape(content[:300])}\n"
    if caption:
        text += f"Подпись: {escape(caption[:300])}\n"

    try:
        await bot.send_message(ADMIN_ID, text, parse_mode=ParseMode.HTML)
    except Exception as e:
        logger.error("notify_debug error: %s", e)


async def forward_broadcast(bot: Bot, chat_id: int, msg: types.Message):
    if msg.text:
        await bot.send_message(chat_id, msg.text)
    elif msg.photo:
        await bot.send_photo(chat_id, photo=msg.photo[-1].file_id, caption=msg.caption)
    elif msg.video:
        await bot.send_video(chat_id, video=msg.video.file_id, caption=msg.caption)
    elif msg.animation:
        await bot.send_animation(
            chat_id, animation=msg.animation.file_id, caption=msg.caption
        )
    elif msg.document:
        await bot.send_document(
            chat_id, document=msg.document.file_id, caption=msg.caption
        )
    elif msg.voice:
        await bot.send_voice(chat_id, voice=msg.voice.file_id, caption=msg.caption)
    elif msg.audio:
        await bot.send_audio(chat_id, audio=msg.audio.file_id, caption=msg.caption)
    elif msg.video_note:
        await bot.send_video_note(chat_id, video_note=msg.video_note.file_id)
    elif msg.sticker:
        await bot.send_sticker(chat_id, sticker=msg.sticker.file_id)
