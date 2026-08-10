import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)
DB_PATH = "house_bot.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Инициализация таблиц базы данных участников.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                name TEXT,
                age INTEGER,
                country TEXT,
                roblox_username TEXT,
                roblox_display_name TEXT,
                roblox_id INTEGER,
                roblox_created TEXT,
                avatar_url TEXT,
                role TEXT DEFAULT 'Участник',
                joined_at TEXT
            )
        """)
        conn.commit()
    logger.info("📦 База данных SQLite инициализирована.")


def add_or_update_member(
    user_id: int,
    username: Optional[str],
    full_name: str,
    name: str,
    age: int,
    country: str,
    roblox_username: str,
    roblox_display_name: str,
    roblox_id: int,
    roblox_created: str,
    avatar_url: str,
    role: str = "Участник"
):
    """
    Добавляет или обновляет данные участника в базе.
    """
    joined_at = datetime.now().strftime("%d.%m.%Y")
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO members (
                user_id, username, full_name, name, age, country,
                roblox_username, roblox_display_name, roblox_id,
                roblox_created, avatar_url, role, joined_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                full_name=excluded.full_name,
                name=excluded.name,
                age=excluded.age,
                country=excluded.country,
                roblox_username=excluded.roblox_username,
                roblox_display_name=excluded.roblox_display_name,
                roblox_id=excluded.roblox_id,
                roblox_created=excluded.roblox_created,
                avatar_url=excluded.avatar_url,
                role=COALESCE(members.role, excluded.role)
        """, (
            user_id, username, full_name, name, age, country,
            roblox_username, roblox_display_name, roblox_id,
            roblox_created, avatar_url, role, joined_at
        ))
        conn.commit()
    logger.info(f"💾 Участник {user_id} ({roblox_username}) сохранен в базе данных.")


def get_member(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Получает информацию об одном участнике.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM members WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_all_members() -> List[Dict[str, Any]]:
    """
    Получает список всех участников хауса.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM members ORDER BY rowid DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def update_member_role(user_id: int, new_role: str) -> bool:
    """
    Обновляет роль участника ('Участник', 'Администратор', 'Создатель').
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE members SET role = ? WHERE user_id = ?", (new_role, user_id))
        conn.commit()
        return cursor.rowcount > 0


def delete_member(user_id: int) -> bool:
    """
    Удаляет участника из базы.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM members WHERE user_id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount > 0


def get_member_count() -> int:
    """
    Количество участников в базе.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM members")
        return cursor.fetchone()[0]
