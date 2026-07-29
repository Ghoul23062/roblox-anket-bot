from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData

class AdminCallback(CallbackData, prefix="admin"):
    """
    Фабрика колбэков для действий администратора (принятие/отклонение заявки).
    """
    action: str  # 'accept' или 'reject'
    user_id: int

def get_start_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура под стартовым сообщением.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Подать анкету", callback_data="start_anketa")]
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
