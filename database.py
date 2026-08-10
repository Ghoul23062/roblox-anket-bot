import sqlite3
import os
import logging

DB_PATH = os.path.join(os.path.dirname(__file__), "house_members.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Инициализирует таблицы базы данных SQLite:
    - members: постоянные утвержденные участники хауса
    - pending_applications: поданные заявки на рассмотрении
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Таблица утвержденных участников
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
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Таблица ожидающих рассмотрения заявок
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pending_applications (
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    logging.info("💾 База данных SQLite успешно инициализирована.")

def save_pending_application(user_id, username, full_name, name, age, country, roblox_username, roblox_display_name, roblox_id, roblox_created, avatar_url):
    """
    Сохраняет поданную анкету в ожидающие заявки (гарантирует сохранение даже при перезапуске сервера).
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO pending_applications (
            user_id, username, full_name, name, age, country,
            roblox_username, roblox_display_name, roblox_id, roblox_created, avatar_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, username, full_name, name, age, country,
        roblox_username, roblox_display_name, roblox_id, roblox_created, avatar_url
    ))
    conn.commit()
    conn.close()

def get_pending_application(user_id):
    """
    Получает данные ожидающей заявки по user_id.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pending_applications WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def add_or_update_member(user_id, username, full_name, name, age, country, roblox_username, roblox_display_name, roblox_id, roblox_created, avatar_url, role="Участник"):
    """
    Добавляет принятого участника в таблицу members и удаляет из pending.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO members (
            user_id, username, full_name, name, age, country,
            roblox_username, roblox_display_name, roblox_id, roblox_created, avatar_url, role
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, username, full_name, name, age, country,
        roblox_username, roblox_display_name, roblox_id, roblox_created, avatar_url, role
    ))
    cursor.execute("DELETE FROM pending_applications WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    logging.info(f"✅ Участник {name} (ID: {user_id}) успешно сохранен в базе!")

def get_all_members():
    """
    Возвращает список всех участников для вкладки «Участники».
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members ORDER BY joined_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_member(user_id):
    """
    Возвращает данные одного участника по user_id.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def update_member_role(user_id, role):
    """
    Обновляет роль участника (например, 'Администратор' или 'Создатель').
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE members SET role = ? WHERE user_id = ?", (role, user_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0

def get_member_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM members")
    count = cursor.fetchone()[0]
    conn.close()
    return count
