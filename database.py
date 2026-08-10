import sqlite3
import json
import os
import logging

DB_PATH = os.path.join(os.path.dirname(__file__), "house_members.db")
JSON_BACKUP_PATH = os.path.join(os.path.dirname(__file__), "house_members.json")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def save_backup_json(members_list):
    """
    Сохраняет всех участников в JSON файл для 100% сохранности при перезапусках Render.
    """
    try:
        with open(JSON_BACKUP_PATH, "w", encoding="utf-8") as f:
            json.dump(members_list, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"Ошибка сохранения JSON бэкапа: {e}")


def load_backup_json():
    """
    Загружает участников из JSON файла при старте.
    """
    if os.path.exists(JSON_BACKUP_PATH):
        try:
            with open(JSON_BACKUP_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Ошибка чтения JSON бэкапа: {e}")
    return []


def init_db():
    """
    Инициализирует таблицы базы данных SQLite и восстанавливает данные из JSON бэкапа.
    """
    conn = get_db_connection()
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
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

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

    # Восстановление из JSON бэкапа
    backup_members = load_backup_json()
    for m in backup_members:
        cursor.execute("""
            INSERT OR REPLACE INTO members (
                user_id, username, full_name, name, age, country,
                roblox_username, roblox_display_name, roblox_id, roblox_created, avatar_url, role
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            m["user_id"], m.get("username", ""), m.get("full_name", ""),
            m.get("name", "Участник"), m.get("age", 0), m.get("country", ""),
            m.get("roblox_username", ""), m.get("roblox_display_name", ""),
            m.get("roblox_id", 0), m.get("roblox_created", ""),
            m.get("avatar_url", ""), m.get("role", "Участник")
        ))
    conn.commit()
    conn.close()
    logging.info(f"💾 База данных SQLite готова. Загружено участников из бэкапа: {len(backup_members)}")


def save_pending_application(user_id, username, full_name, name, age, country, roblox_username, roblox_display_name, roblox_id, roblox_created, avatar_url):
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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pending_applications WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def add_or_update_member(user_id, username, full_name, name, age, country, roblox_username, roblox_display_name, roblox_id, roblox_created, avatar_url, role="Участник"):
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

    # Обновляем JSON бэкап
    save_backup_json(get_all_members())
    logging.info(f"✅ Участник {name} ({role}) сохранен в SQLite и JSON бэкап!")


def get_all_members():
    """
    Возвращает список всех участников, отсортированный по важности роли:
    1. Создатель
    2. Администратор
    3. Монтажёр
    4. Участник
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM members 
        ORDER BY 
            CASE role 
                WHEN 'Создатель' THEN 1 
                WHEN 'Администратор' THEN 2 
                WHEN 'Монтажёр' THEN 3
                WHEN 'Монтажер' THEN 3
                ELSE 4 
            END,
            joined_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_member(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def update_member_role(user_id, role):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE members SET role = ? WHERE user_id = ?", (role, user_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    if affected > 0:
        save_backup_json(get_all_members())
    return affected > 0


def get_member_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM members")
    count = cursor.fetchone()[0]
    conn.close()
    return count
