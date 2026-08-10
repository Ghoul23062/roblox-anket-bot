import html
import logging
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config import ADMIN_CHAT_ID, HOUSE_CHAT_ID
from states import Questionnaire
from keyboards import (
    get_start_keyboard,
    get_confirm_keyboard,
    get_admin_keyboard,
    AdminCallback,
)
from logger_bot import send_log

logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    """
    Обработчик команды /start. Приветствие и кнопка подачи анкеты.
    """
    await state.clear()
    user = message.from_user
    user_mention = f"@{user.username}" if user.username else f'<a href="tg://user?id={user.id}">{html.escape(user.full_name)}</a>'

    welcome_text = (
        "👋 <b>Привет! Добро пожаловать в бот Roblox-хауса!</b>\n\n"
        "Здесь ты можешь подать заявку на вступление в наш закрытый хаус. "
        "Заполнение анкеты займет всего пару минут.\n\n"
        "Нажми кнопку ниже, чтобы начать! 👇"
    )
    await message.answer(welcome_text, reply_markup=get_start_keyboard())

    # Скрытый лог запуска бота пользователем
    await send_log(
        bot,
        f"👋 <b>[ЛОГ] Запуск бота (/start)</b>\n\n"
        f"👤 <b>Пользователь:</b> {user_mention}\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>"
    )


@router.callback_query(F.data == "start_anketa")
async def start_questionnaire(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Начало заполнения анкеты по кнопке «📝 Подать анкету».
    """
    await state.clear()
    await state.set_state(Questionnaire.name)
    await callback.message.answer("Шаг 1 из 4: <b>Как тебя зовут?</b> 👤")
    await callback.answer()

    user = callback.from_user
    user_mention = f"@{user.username}" if user.username else f'<a href="tg://user?id={user.id}">{html.escape(user.full_name)}</a>'
    
    # Скрытый лог начала анкеты
    await send_log(
        bot,
        f"📝 <b>[ЛОГ] Начато заполнение анкеты</b>\n\n"
        f"👤 <b>Пользователь:</b> {user_mention}\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>"
    )


@router.message(Questionnaire.name)
async def process_name(message: Message, state: FSMContext):
    """
    Шаг 1: Получение имени.
    """
    if not message.text:
        await message.answer("Пожалуйста, введи свое имя текстом:")
        return

    name = message.text.strip()
    await state.update_data(name=name)
    await state.set_state(Questionnaire.age)
    await message.answer("Шаг 2 из 4: <b>Сколько тебе лет?</b> 🎂")


@router.message(Questionnaire.age)
async def process_age(message: Message, state: FSMContext):
    """
    Шаг 2: Получение и валидация возраста (число от 7 до 99).
    """
    if not message.text or not message.text.isdigit():
        await message.answer("⚠️ Пожалуйста, введи возраст числом (например, 14):")
        return

    age = int(message.text)
    if age < 7 or age > 99:
        await message.answer("⚠️ Пожалуйста, введи корректный возраст (от 7 до 99 лет):")
        return

    await state.update_data(age=age)
    await state.set_state(Questionnaire.country)
    await message.answer("Шаг 3 из 4: <b>Из какой ты страны?</b> 🌍")


@router.message(Questionnaire.country)
async def process_country(message: Message, state: FSMContext):
    """
    Шаг 3: Получение страны.
    """
    if not message.text:
        await message.answer("Пожалуйста, укажи страну текстом:")
        return

    country = message.text.strip()
    await state.update_data(country=country)
    await state.set_state(Questionnaire.photo)
    await message.answer("Шаг 4 из 4: <b>Отправь скриншот/фото своего скина в Roblox</b> 📸")


@router.message(Questionnaire.photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    """
    Шаг 4: Успешное получение фотографии скина и вывод предпросмотра карточки.
    """
    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)
    await state.set_state(Questionnaire.confirm)

    data = await state.get_data()

    card_text = (
        "📋 <b>Проверь свои данные перед отправкой:</b>\n\n"
        f"👤 <b>Имя:</b> {html.escape(data['name'])}\n"
        f"🎂 <b>Возраст:</b> {data['age']}\n"
        f"🌍 <b>Страна:</b> {html.escape(data['country'])}\n\n"
        "Всё верно? Нажми <b>«✅ Отправить заявку»</b> или <b>«🔄 Заполнить заново»</b>."
    )

    await message.answer_photo(
        photo=photo_id,
        caption=card_text,
        reply_markup=get_confirm_keyboard()
    )


@router.message(Questionnaire.photo, ~F.photo)
async def process_photo_invalid(message: Message):
    """
    Шаг 4: Валидация — если отправлено не фото (текст, документ и т.д.).
    """
    await message.answer("⚠️ Ошибка! Пожалуйста, отправь именно <b>фотографию</b> или <b>скриншот</b> (как фото, а не файл/документ) твоего скина в Roblox.")


@router.callback_query(F.data == "restart_anketa")
async def restart_questionnaire(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Сброс FSM и перезапуск анкеты с первого шага.
    """
    await state.clear()
    await state.set_state(Questionnaire.name)
    await callback.message.answer("🔄 Перезапуск анкеты!\n\nШаг 1 из 4: <b>Как тебя зовут?</b> 👤")
    await callback.answer("Анкета сброшена")

    user = callback.from_user
    user_mention = f"@{user.username}" if user.username else f'<a href="tg://user?id={user.id}">{html.escape(user.full_name)}</a>'
    await send_log(
        bot,
        f"🔄 <b>[ЛОГ] Анкета сброшена на 1 шаг</b>\n\n"
        f"👤 <b>Пользователь:</b> {user_mention}\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>"
    )


@router.callback_query(F.data == "send_anketa", Questionnaire.confirm)
async def send_questionnaire(callback: CallbackQuery, state: FSMContext, bot: Bot):
    """
    Подтверждение и отправка анкеты в админ-чат.
    """
    data = await state.get_data()
    user = callback.from_user

    # Формирование ссылки или упоминания профиля Telegram
    if user.username:
        tg_profile = f"@{user.username}"
    else:
        tg_profile = f'<a href="tg://user?id={user.id}">{html.escape(user.full_name)}</a>'

    admin_caption = (
        "📥 <b>Новая заявка в Roblox Хаус!</b>\n\n"
        f"👤 <b>Имя:</b> {html.escape(str(data.get('name')))}\n"
        f"🎂 <b>Возраст:</b> {data.get('age')}\n"
        f"🌍 <b>Страна:</b> {html.escape(str(data.get('country')))}\n"
        f"🔗 <b>Профиль TG:</b> {tg_profile}\n"
        f"🆔 <b>User ID:</b> <code>{user.id}</code>"
    )

    if not ADMIN_CHAT_ID:
        logger.error("ADMIN_CHAT_ID не настроен!")
        await callback.message.answer("❌ Ошибка настройки бота: не указан ADMIN_CHAT_ID.")
        await callback.answer()
        return

    try:
        # Отправка фото скина с подписью и кнопками в админ-чат
        await bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=data['photo'],
            caption=admin_caption,
            reply_markup=get_admin_keyboard(user.id)
        )
        await callback.message.answer("Ваша заявка отправлена на рассмотрение администраторам! ⏳")
        await state.clear()
        await callback.answer("Заявка отправлена!")

        # Дублирование лога в скрытый канал
        log_text = (
            "📥 <b>[ЛОГ] Новая заявка отправлена в админ-чат</b>\n\n"
            f"👤 <b>Имя:</b> {html.escape(str(data.get('name')))}\n"
            f"🎂 <b>Возраст:</b> {data.get('age')}\n"
            f"🌍 <b>Страна:</b> {html.escape(str(data.get('country')))}\n"
            f"🔗 <b>TG:</b> {tg_profile}\n"
            f"🆔 <b>ID:</b> <code>{user.id}</code>"
        )
        await send_log(bot, log_text, photo=data['photo'])

    except Exception as e:
        logger.error(f"Ошибка при отправке заявки в админ-чат: {e}")
        await callback.message.answer("❌ Не удалось отправить заявку. Пожалуйста, попробуйте позже.")
        await callback.answer("Ошибка при отправке", show_alert=True)
        await send_log(
            bot,
            f"⚠️ <b>[ОШИБКА] Не удалось отправить заявку в админ-чат</b>\n\n"
            f"👤 <b>Кандидат:</b> {tg_profile} (<code>{user.id}</code>)\n"
            f"❗ <b>Ошибка:</b> <code>{html.escape(str(e))}</code>"
        )


@router.callback_query(AdminCallback.filter())
async def handle_admin_decision(
    callback: CallbackQuery,
    callback_data: AdminCallback,
    bot: Bot
):
    """
    Обработчик кнопок администратора [✅ Принять] и [❌ Отклонить].
    """
    action = callback_data.action
    applicant_id = callback_data.user_id
    admin_user = callback.from_user

    if admin_user.username:
        admin_mention = f"@{admin_user.username}"
    else:
        admin_mention = f'<a href="tg://user?id={admin_user.id}">{html.escape(admin_user.full_name)}</a>'

    original_caption = callback.message.caption or ""

    if action == "accept":
        if not HOUSE_CHAT_ID:
            await callback.answer("❌ Ошибка: HOUSE_CHAT_ID не указан в конфигурации!", show_alert=True)
            return

        try:
            # Генерация персональной одноразовой ссылки на вступление (member_limit=1)
            invite_link = await bot.create_chat_invite_link(
                chat_id=HOUSE_CHAT_ID,
                member_limit=1
            )

            # Отправка пользователю ссылки в ЛС
            await bot.send_message(
                chat_id=applicant_id,
                text=(
                    "Поздравляем! Твоя заявка в Roblox-хаус одобрена! 🎉\n"
                    f"Вот твоя личная одноразовая ссылка для входа в чат: {invite_link.invite_link}"
                )
            )

            # Обновление сообщения в админ-чате
            new_caption = (
                f"{original_caption}\n\n"
                f"✅ <b>Заявка принята</b> администратором {admin_mention}"
            )
            await callback.message.edit_caption(caption=new_caption, reply_markup=None)
            await callback.answer("Заявка успешно принята!")

            # Скрытый лог принятия
            await send_log(
                bot,
                f"✅ <b>[РЕШЕНИЕ] Заявка ПРИНЯТА</b>\n\n"
                f"👑 <b>Администратор:</b> {admin_mention}\n"
                f"👤 <b>Кандидат ID:</b> <code>{applicant_id}</code>\n"
                f"🔗 <b>Сгенерированная ссылка:</b> {invite_link.invite_link}"
            )

        except Exception as e:
            logger.error(f"Ошибка при принятии заявки для {applicant_id}: {e}")
            await callback.answer(
                "❌ Ошибка! Проверьте, добавлен ли бот в хаус-чат с правами создания пригласительных ссылок.",
                show_alert=True
            )
            await send_log(
                bot,
                f"⚠️ <b>[ОШИБКА] Сбой при принятии заявки</b>\n\n"
                f"👑 <b>Администратор:</b> {admin_mention}\n"
                f"👤 <b>Кандидат ID:</b> <code>{applicant_id}</code>\n"
                f"❗ <b>Ошибка:</b> <code>{html.escape(str(e))}</code>"
            )

    elif action == "reject":
        try:
            # Отправка уведомления пользователю
            await bot.send_message(
                chat_id=applicant_id,
                text="К сожалению, твоя заявка в Roblox-хаус была отклонена. 😔"
            )

            # Обновление сообщения в админ-чате
            new_caption = (
                f"{original_caption}\n\n"
                f"❌ <b>Заявка отклонена</b> администратором {admin_mention}"
            )
            await callback.message.edit_caption(caption=new_caption, reply_markup=None)
            await callback.answer("Заявка отклонена!")

            # Скрытый лог отклонения
            await send_log(
                bot,
                f"❌ <b>[РЕШЕНИЕ] Заявка ОТКЛОНЕНА</b>\n\n"
                f"👑 <b>Администратор:</b> {admin_mention}\n"
                f"👤 <b>Кандидат ID:</b> <code>{applicant_id}</code>"
            )

        except Exception as e:
            logger.error(f"Ошибка при отклонении заявки для {applicant_id}: {e}")
            new_caption = (
                f"{original_caption}\n\n"
                f"❌ <b>Заявка отклонена</b> администратором {admin_mention} (не удалось отправить ЛС пользователю)"
            )
            await callback.message.edit_caption(caption=new_caption, reply_markup=None)
            await callback.answer("Заявка отклонена (пользователь заблокировал бота).")

            await send_log(
                bot,
                f"❌ <b>[РЕШЕНИЕ] Заявка ОТКЛОНЕНА (с предупреждением)</b>\n\n"
                f"👑 <b>Администратор:</b> {admin_mention}\n"
                f"👤 <b>Кандидат ID:</b> <code>{applicant_id}</code>\n"
                f"⚠️ <i>Не удалось доставить ЛС пользователю (возможно бот заблокирован)</i>"
            )
