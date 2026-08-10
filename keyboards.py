from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters.callback_data import CallbackData
from config import WEBAPP_URL

class AdminCallback(CallbackData, prefix="admin"):
    """
    Фабрика колбэков для действий администратора (принятие/отклонение заявки).
    """
    action: str  # 'accept' или 'reject'
    user_id: int

def get_start_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура под стартовым сообщением с кнопкой подачи анкеты и кнопкой открытия Mini App.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📱 Открыть Хаус Апп",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ],
            [
                InlineKeyboardButton(
                    text="📝 Подать анкету",
                    callback_data="start_anketa"
                )
            ]
        ]
    )

def get_confirm_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура предпросмотра анкеты пользователем.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Отправить заявку", callback_data="send_anketa"),
                InlineKeyboardButton(text="🔄 Заполнить заново", callback_data="restart_anketa")
            ]
        ]
    )

def get_admin_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для администраторов под карточкой заявки.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Принять",
                    callback_data=AdminCallback(action="accept", user_id=user_id).pack()
                ),
                InlineKeyboardButton(
                    text="❌ Отклонить",
                    callback_data=AdminCallback(action="reject", user_id=user_id).pack()
                )
            ]
        ]
    )


class AdminBanCallback(CallbackData, prefix="admin_ban"):
    """
    Фабрика колбэков для быстрого бана из списка участников.
    """
    user_id: int


def get_members_moderation_keyboard(members: list) -> InlineKeyboardMarkup:
    """
    Генерирует инлайн-кнопки бана для списка участников хауса.
    """
    buttons = []
    for m in members[:20]:  # до 20 участников на страницу
        user_id = m.get("user_id", 0)
        name = m.get("name") or m.get("roblox_username") or f"ID {user_id}"
        role = m.get("role", "Участник")
        
        # Не показываем кнопку бана для Создателя
        if role == "Создатель":
            continue
            
        btn_text = f"🚫 Забанить {name}"
        buttons.append([
            InlineKeyboardButton(
                text=btn_text,
                callback_data=AdminBanCallback(user_id=user_id).pack()
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
