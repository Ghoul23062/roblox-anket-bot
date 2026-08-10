import asyncio
import io
import json
import logging
import os
import sys
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import MenuButtonWebApp, WebAppInfo

from config import BOT_TOKEN, WEBAPP_URL
from handlers import router
from logger_bot import send_log
from database import init_db, get_all_members, get_member


# ================== HTTP API & WEBAPP HANDLERS ==================

async def handle_health_check(request):
    """
    Эндпоинт проверки работоспособности для Render.
    """
    return web.Response(text="Roblox House Bot is running 24/7!", status=200)


async def handle_webapp_index(request):
    """
    Отдает главную страницу Mini App (index.html) в кодировке UTF-8.
    """
    index_path = os.path.join(os.path.dirname(__file__), "webapp", "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        return web.Response(text=content, content_type="text/html", charset="utf-8")
    return web.Response(text="WebApp index.html not found", status=404)


async def handle_api_members(request):
    """
    API: Список всех участников хауса.
    """
    members = get_all_members()
    return web.json_response(members)


async def handle_api_member(request):
    """
    API: Получение данных одного участника по ?user_id=123.
    """
    user_id_raw = request.query.get("user_id", "0")
    try:
        user_id = int(user_id_raw)
    except ValueError:
        return web.json_response({"found": False, "error": "Invalid user_id"})

    member = get_member(user_id)
    if member:
        return web.json_response({"found": True, "member": member})
    return web.json_response({"found": False})


async def start_web_server():
    """
    Запуск фонового веб-сервера для Telegram Mini App и Render Web Service.
    """
    port = int(os.getenv("PORT", 8080))
    app = web.Application()

    # API маршруты
    app.router.add_get("/api/members", handle_api_members)
    app.router.add_get("/api/member", handle_api_member)
    
    # WebApp маршруты
    app.router.add_get("/webapp", handle_webapp_index)
    app.router.add_get("/webapp/", handle_webapp_index)
    app.router.add_get("/", handle_webapp_index)
    app.router.add_get("/health", handle_health_check)

    # Статические файлы (на случай прямого обращения к .css / .js)
    webapp_dir = os.path.join(os.path.dirname(__file__), "webapp")
    if os.path.exists(webapp_dir):
        app.router.add_static("/webapp/", path=webapp_dir, name="webapp_static")
        app.router.add_static("/static/", path=webapp_dir, name="static")

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"🌐 WebApp & API сервер запущен на порту {port} (URL: {WEBAPP_URL})")


# ================== ЗАПУСК БОТА ==================

async def main():
    """
    Основная функция запуска бота, БД и веб-сервера.
    """
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

    # 1. Инициализация базы данных SQLite
    init_db()

    # 2. Запуск веб-сервера для Mini App и Render
    await start_web_server()

    # 3. Инициализация бота с парсингом HTML
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Установка постоянной кнопки меню Mini App в Telegram
    try:
        await bot.set_chat_menu_button(
            menu_button=MenuButtonWebApp(
                text="📱 Хаус Апп",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        )
    except Exception as e:
        logging.warning(f"Не удалось установить MenuButton WebApp: {e}")

    # 4. Инициализация диспетчера
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    logging.info("🚀 Запуск Roblox-house анкетного бота...")

    await bot.delete_webhook(drop_pending_updates=True)
    await send_log(bot, "🟢 <b>Roblox House Бот & Mini App успешно запущены!</b>")

    try:
        await dp.start_polling(bot)
    finally:
        await send_log(bot, "🔴 <b>Roblox House Бот остановлен!</b>")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("🛑 Бот остановлен.")
