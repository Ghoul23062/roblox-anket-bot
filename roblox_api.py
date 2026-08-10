import aiohttp
import logging
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

USER_LOOKUP_URL = "https://users.roblox.com/v1/usernames/users"
USER_DETAILS_URL = "https://users.roblox.com/v1/users/{user_id}"
USER_AVATAR_URL = "https://thumbnails.roblox.com/v1/users/avatar?userIds={user_id}&size=720x720&format=Png&isCircular=false"


async def get_roblox_user(username: str) -> Optional[Dict[str, Any]]:
    """
    Получает информацию об игроке в Roblox по никнейму:
    - Проверяет существование
    - Получает ID, никнейм и отображаемое имя (DisplayName)
    - Получает дату создания аккаунта
    - Получает HD-рендер аватара (скина)
    """
    clean_username = username.strip().replace("@", "")
    if not clean_username:
        return None

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            # 1. Поиск User ID по никнейму
            payload = {
                "usernames": [clean_username],
                "excludeBannedUsers": False
            }
            async with session.post(USER_LOOKUP_URL, json=payload) as resp:
                if resp.status != 200:
                    logger.error(f"Roblox API username lookup failed with status {resp.status}")
                    return None
                data = await resp.json()

            user_list = data.get("data", [])
            if not user_list:
                return None

            user_data = user_list[0]
            user_id = user_data["id"]
            name = user_data["name"]
            display_name = user_data.get("displayName", name)

            # 2. Получение детальной информации (дата регистрации)
            created_str = "Неизвестно"
            async with session.get(USER_DETAILS_URL.format(user_id=user_id)) as resp:
                if resp.status == 200:
                    details = await resp.json()
                    created_raw = details.get("created")
                    if created_raw:
                        try:
                            # Парсинг ISO формата даты (например 2021-05-14T12:00:00.000Z)
                            dt = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
                            created_str = dt.strftime("%d.%m.%Y")
                        except Exception:
                            created_str = created_raw[:10]

            # 3. Получение официального 3D/HD аватара (скина)
            avatar_url = "https://tr.rbxcdn.com/30DAY-Avatar-720x720.png"
            async with session.get(USER_AVATAR_URL.format(user_id=user_id)) as resp:
                if resp.status == 200:
                    avatar_data = await resp.json()
                    avatar_list = avatar_data.get("data", [])
                    if avatar_list and avatar_list[0].get("imageUrl"):
                        avatar_url = avatar_list[0]["imageUrl"]

            return {
                "id": user_id,
                "name": name,
                "displayName": display_name,
                "created_date": created_str,
                "avatar_url": avatar_url,
                "profile_url": f"https://www.roblox.com/users/{user_id}/profile"
            }

    except Exception as e:
        logger.error(f"Ошибка при запросе к Roblox API для пользователя '{clean_username}': {e}")
        return None
