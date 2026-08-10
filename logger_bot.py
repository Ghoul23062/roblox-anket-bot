import logging
from typing import Optional
from aiogram import Bot
from config import LOG_CHANNEL_ID

logger = logging.getLogger(__name__)


async def send_log(
    bot: Bot,
    text: str,
    photo: Optional[str] = None
):
    """
    Безопасная отправка скрытого лога в специальный канал/группу аудита.
    Если LOG_CHANNEL_ID не задан или бот не имеет прав, логирование не ломает работу бота.
    """
    if not LOG_CHANNEL_ID:
        return

    try:
        if photo:
            await bot.send_photo(
                chat_id=LOG_CHANNEL_ID,
                photo=photo,
                caption=text
            )
        else:
            await bot.send_message(
                chat_id=LOG_CHANNEL_ID,
                text=text,
                disable_web_page_preview=True
            )
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение в канал логов ({LOG_CHANNEL_ID}): {e}")
