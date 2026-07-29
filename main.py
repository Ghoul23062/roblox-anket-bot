import asyncio
import io
import logging
import os
import sys
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import router


async def handle_health_check(request):
    """
    Эндпоинт проверки работоспособности (поддерживает любой HTTP-метод: GET, HEAD и т.д.).
    """
    return web.Response(text="Roblox House Bot is running 24/7!", status=200)


async def start_web_server():
    """
    Запуск легкого HTTP-сервера для Render Web Service (Free Tier).
    """
    port = int(os.getenv("PORT", 8080))
    app = web.Application()
    # Разрешаем любые пути и любые HTTP-методы (GET, HEAD)
    app.router.add_route("*", "/{tail:.*}", handle_health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"🌐 HTTP Health Check сервер запущен на порту {port}")


async def main():
    """
    Основная функция запуска бота и веб-сервера.
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

    # Запуск фонового веб-сервера для бесплатного тарифа Render
    await start_web_server()

    # Инициализация бота с парсингом HTML по умолчанию
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Инициализация диспетчера с FSM
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
