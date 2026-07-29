import asyncio
import io
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import router


async def main():
    """
    Основная функция запуска бота и инициализации диспетчера.
    """
    # Настройка кодировки UTF-8 для Windows консоли
    if sys.platform == "win32":
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        except Exception:
            pass

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        stream=sys.stdout
    )

    if not BOT_TOKEN:
        logging.critical("❌ BOT_TOKEN отсутствует в конфигурации! Проверьте файл .env")
        return

    # Инициализация бота с парсингом HTML по умолчанию (aiogram 3.x)
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Инициализация диспетчера с FSM в оперативной памяти
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    logging.info("🚀 Запуск Roblox-house анкетного бота...")

    # Сброс накопленных обновлений и запуск polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Бот остановлен.")
