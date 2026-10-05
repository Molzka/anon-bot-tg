import asyncio
import logging
from enum import Enum

from aiogram import Bot, types
from aiogram.exceptions import (
    TelegramAPIError,
    TelegramForbiddenError,
    TelegramNetworkError,
    TelegramRetryAfter,
    TelegramServerError,
)

logger = logging.getLogger(__name__)
MAX_SEND_ATTEMPTS = 3
MAX_RETRY_AFTER = 30


class DeliveryStatus(Enum):
    SENT = "sent"
    BLOCKED = "blocked"
    TEMPORARY_ERROR = "temporary_error"
    FAILED = "failed"
    UNSUPPORTED = "unsupported"


def extract_media(msg: types.Message):
    if msg.text:
        return "text", msg.text, None, None
    if msg.photo:
        return "photo", None, msg.photo[-1].file_id, msg.caption
    for kind in ("animation", "video", "document", "voice", "audio", "video_note", "sticker"):
        media = getattr(msg, kind)
        if media:
            caption = msg.caption if kind not in ("video_note", "sticker") else None
            return kind, None, media.file_id, caption
    return None, None, None, None


def split_text(text: str, limit: int = 4096) -> list[str]:
    chunks = []
    start = units = 0
    for index, character in enumerate(text):
        size = 2 if ord(character) > 0xFFFF else 1
        if units + size > limit:
            chunks.append(text[start:index])
            start, units = index, 0
        units += size
    if start < len(text):
        chunks.append(text[start:])
    return chunks


async def send_with_retry(send, **kwargs):
    for attempt in range(MAX_SEND_ATTEMPTS):
        try:
            return await send(**kwargs)
        except TelegramRetryAfter as exc:
            if attempt == MAX_SEND_ATTEMPTS - 1 or exc.retry_after > MAX_RETRY_AFTER:
                raise
            await asyncio.sleep(exc.retry_after)
        except (TelegramNetworkError, TelegramServerError):
            if attempt == MAX_SEND_ATTEMPTS - 1:
                raise
            await asyncio.sleep(2 ** attempt)


async def send_text(bot: Bot, chat_id: int, text: str, reply_markup=None):
    chunks = split_text(text)
    for index, chunk in enumerate(chunks):
        await send_with_retry(
            bot.send_message,
            chat_id=chat_id,
            text=chunk,
            parse_mode=None,
            reply_markup=reply_markup if index == len(chunks) - 1 else None,
        )


async def deliver(
    bot: Bot,
    chat_id: int,
    msg: types.Message,
    header: str,
    reply_markup=None,
) -> DeliveryStatus:
    kind, content, file_id, caption = extract_media(msg)
    if kind is None:
        return DeliveryStatus.UNSUPPORTED
    try:
        if kind == "text":
            await send_text(bot, chat_id, header + content, reply_markup)
        elif kind in ("video_note", "sticker"):
            if header:
                await send_text(bot, chat_id, header)
            await send_with_retry(
                getattr(bot, f"send_{kind}"), chat_id=chat_id,
                **{kind: file_id}, reply_markup=reply_markup,
            )
        else:
            combined = header + (caption or "")
            overflow = len(combined.encode("utf-16-le")) // 2 > 1024
            await send_with_retry(
                getattr(bot, f"send_{kind}"), chat_id=chat_id,
                **{kind: file_id}, caption=header if overflow else combined,
                parse_mode=None, reply_markup=None if overflow else reply_markup,
            )
            if overflow:
                await send_text(bot, chat_id, caption or "", reply_markup)
        return DeliveryStatus.SENT
    except TelegramForbiddenError as exc:
        status = DeliveryStatus.BLOCKED
        error_type = type(exc).__name__
    except (TelegramRetryAfter, TelegramNetworkError, TelegramServerError) as exc:
        status = DeliveryStatus.TEMPORARY_ERROR
        error_type = type(exc).__name__
    except TelegramAPIError as exc:
        status = DeliveryStatus.FAILED
        error_type = type(exc).__name__

    logger.warning("Delivery failed (%s)", error_type)
    return status


async def forward_broadcast(bot: Bot, chat_id: int, msg: types.Message) -> DeliveryStatus:
    return await deliver(bot, chat_id, msg, header="")
