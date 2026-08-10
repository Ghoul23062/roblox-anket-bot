import os
import logging
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_CHAT_ID_RAW = os.getenv("ADMIN_CHAT_ID", "0").strip()
HOUSE_CHAT_ID_RAW = os.getenv("HOUSE_CHAT_ID", "0").strip()
LOG_CHANNEL_ID_RAW = os.getenv("LOG_CHANNEL_ID", "0").strip()

if not BOT_TOKEN:
    logging.warning("⚠️ BOT_TOKEN is missing! Please set BOT_TOKEN in .env or environment variables.")

try:
    ADMIN_CHAT_ID = int(ADMIN_CHAT_ID_RAW)
except ValueError:
    logging.error("⚠️ ADMIN_CHAT_ID must be an integer! Check your .env file.")
    ADMIN_CHAT_ID = 0

try:
    HOUSE_CHAT_ID = int(HOUSE_CHAT_ID_RAW)
except ValueError:
    logging.error("⚠️ HOUSE_CHAT_ID must be an integer! Check your .env file.")
    HOUSE_CHAT_ID = 0

try:
    LOG_CHANNEL_ID = int(LOG_CHANNEL_ID_RAW)
except ValueError:
    logging.error("⚠️ LOG_CHANNEL_ID must be an integer! Check your .env file.")
    LOG_CHANNEL_ID = 0
