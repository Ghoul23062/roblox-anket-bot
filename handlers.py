import html
import logging
from aiogram import Router, F, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

from config import ADMIN_CHAT_ID, HOUSE_CHAT_ID, WEBAPP_URL
from states import Questionnaire
from keyboards import (
    get_start_keyboard,
    get_confirm_keyboard,
    get_admin_keyboard,
    AdminCallback,
)
from logger_bot import send_log
from roblox_api import get_roblox_user
from database import (
    add_or_update_member,
    save_pending_application,
    get_pending_application,
    update_member_role,
    get_member_count,
    get_all_members
)

logger = logging.getLogger(__name__)

router = Router()

PENDING_APPLICATIONS = {}


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    """
    Обработчик команды /start в ЛС бота.
    """
    await state.clear()
    user = message.from_user
    user_mention = f"@{user.username}" if user.username else f'<a href="tg://user?id={user.id}">{html.escape(user.full_name)}</a>'

    welcome_text = (
        "👋 <b>Добро пожаловать в хаус NEON BLUR!</b> 💖\n\n"
        "Здесь ты можешь открыть наше <b>фирменное мини-приложение</b> или подать анкету на вступление в наш Roblox-хаус.\n\n"
        "Выбирай действие ниже! 👇"
    )
    await message.answer(welcome_text, reply_markup=get_start_keyboard())

    await send_log(
        bot,
        f"👋 <b>[ЛОГ] Запуск бота (/start)</b>\n\n"
        f"👤 <b>Пользователь:</b> {user_mention}\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>"
    )


@router.message(Command("app", "house", "menu"))
async def cmd_open_app(message: Message):
    """
    Команда /app, /house или /menu (работает как в ЛС, так и в групповом чате хауса).
    """
    count = get_member_count()
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💖 Открыть NEON BLUR App", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
    )
    text = (
        "🏰 <b>NEON BLUR • Официальное приложение хауса</b>\n\n"
        f"👥 Участников в хаусе: <b>{count}</b>\n"
        "🎮 Игры: <b>MM2</b> и <b>TTD 3</b>\n\n"
        "<i>Нажми кнопку ниже, чтобы открыть 3D профили и список тусовки:</i>"
    )
    await message.answer(text, reply_markup=kb)


@router.message(Command("iamcreator"))
async def cmd_iam_creator(message: Message):
    """
    Быстрая регистрация создателя хауса: /iamcreator <roblox_nick>
    """
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("⚠️ Использование: <code>/iamcreator ТвойRobloxНик</code>\nПример: <code>/iamcreator Builderman</code>")
        return

    roblox_nick = args[1].strip()
    status_msg = await message.answer("🔍 <i>Ищу твой профиль в Roblox...</i>")

    r = await get_roblox_user(roblox_nick)
    if not r:
        await status_msg.edit_text(f"❌ Ник Roblox «{html.escape(roblox_nick)}» не найден!")
        return

    user = message.from_user
    add_or_update_member(
        user_id=user.id,
        username=user.username or "",
        full_name=user.full_name or "Создатель",
        name=user.first_name or "Создатель",
        age=0,
        country="Не указана",
        roblox_username=r["name"],
        roblox_display_name=r["displayName"],
        roblox_id=r["id"],
        roblox_created=r["created_date"],
        avatar_url=r["avatar_url"],
        role="Создатель"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👑 Открыть свой VIP профиль", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
    )
    await status_msg.edit_text(
        f"👑 <b>Ты успешно добавлен как СОЗДАТЕЛЬ хауса!</b>\n\n"
        f"🎮 Roblox: <b>{html.escape(r['name'])}</b>\n"
        f"🆔 ID: <code>{r['id']}</code>\n"
        "Твой профиль теперь сияет золотом и стоит на 1 месте в приложении! 🌟",
        reply_markup=kb
    )


@router.message(Command("iamadmin"))
async def cmd_iam_admin(message: Message):
    """
    Быстрая регистрация администратора: /iamadmin <roblox_nick>
    """
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("⚠️ Использование: <code>/iamadmin ТвойRobloxНик</code>\nПример: <code>/iamadmin Builderman</code>")
        return

    roblox_nick = args[1].strip()
    status_msg = await message.answer("🔍 <i>Ищу твой профиль в Roblox...</i>")

    r = await get_roblox_user(roblox_nick)
    if not r:
        await status_msg.edit_text(f"❌ Ник Roblox «{html.escape(roblox_nick)}» не найден!")
        return

    user = message.from_user
    add_or_update_member(
        user_id=user.id,
        username=user.username or "",
        full_name=user.full_name or "Администратор",
        name=user.first_name or "Администратор",
        age=0,
        country="Не указана",
        roblox_username=r["name"],
        roblox_display_name=r["displayName"],
        roblox_id=r["id"],
        roblox_created=r["created_date"],
        avatar_url=r["avatar_url"],
        role="Администратор"
    )

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛡️ Открыть свой профиль", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
    )
    await status_msg.edit_text(
        f"🛡️ <b>Ты успешно добавлен как АДМИНИСТРАТОР хауса!</b>\n\n"
        f"🎮 Roblox: <b>{html.escape(r['name'])}</b>\n"
        f"🆔 ID: <code>{r['id']}</code>\n"
        "Твой профиль теперь выделяется неоново-розовым цветом в приложении! 💖",
        reply_markup=kb
    )


@router.message(Command("members"))
async def cmd_members_list(message: Message):
    """
    Команда /members в группе или ЛС.
    """
    members = get_all_members()
    count = len(members)
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👥 Открыть список в App", web_app=WebAppInfo(url=WEBAPP_URL))]
        ]
    )
    if count == 0:
        await message.answer("👥 В базе пока нет утвержденных участников.", reply_markup=kb)
        return

    text = f"👥 <b>Участники хауса NEON BLUR (Всего: {count}):</b>\n\n"
    for i, m in enumerate(members[:15], 1):
        role_icon = "👑" if m.get("role") == "Создатель" else ("🛡️" if m.get("role") == "Администратор" else "✨")
        text += f"{i}. {role_icon} <b>{html.escape(m.get('name', ''))}</b> (@{html.escape(m.get('roblox_username', ''))})\n"

    if count > 15:
        text += f"\n<i>...и ещё {count - 15} участников!</i>"

    await message.answer(text, reply_markup=kb)


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
    Шаг 2: Получение и валидация возраста.
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
    await state.set_state(Questionnaire.roblox_username)
    await message.answer(
        "Шаг 4 из 4: <b>Введи свой никнейм в Roblox</b> 🎮\n"
        "<i>(Бот автоматически найдет твой профиль и скин, например: Builderman)</i>"
    )


@router.message(Questionnaire.roblox_username)
async def process_roblox_username(message: Message, state: FSMContext):
    """
    Шаг 4: Проверка никнейма через Roblox API.
    """
    if not message.text:
        await message.answer("⚠️ Пожалуйста, отправь свой никнейм в Roblox текстом:")
        return

    username = message.text.strip()
    status_msg = await message.answer("🔍 <i>Ищу твой аккаунт в Roblox...</i>")

    roblox_data = await get_roblox_user(username)

    if not roblox_data:
        await status_msg.edit_text(
            f"❌ Игрок с ником <b>«{html.escape(username)}»</b> не найден в Roblox!\n\n"
            "Пожалуйста, проверь правильность написания и введи никнейм ещё раз:"
        )
        return

    try:
        await status_msg.delete()
    except Exception:
        pass

    await state.update_data(roblox=roblox_data)
    await state.set_state(Questionnaire.confirm)

    data = await state.get_data()
    r = data['roblox']

    card_text = (
        "📋 <b>Проверь свои данные перед отправкой:</b>\n\n"
        f"👤 <b>Имя:</b> {html.escape(data['name'])}\n"
        f"🎂 <b>Возраст:</b> {data['age']}\n"
        f"🌍 <b>Страна:</b> {html.escape(data['country'])}\n"
        f"🎮 <b>Roblox Ник:</b> <a href=\"{r['profile_url']}\">{html.escape(r['name'])}</a> ({html.escape(r['displayName'])})\n"
        f"🆔 <b>Roblox ID:</b> <code>{r['id']}</code>\n"
        f"📅 <b>Дата регистрации в Roblox:</b> {r['created_date']}\n\n"
        "Всё верно? Нажми <b>«✅ Отправить заявку»</b> или <b>«🔄 Заполнить заново»</b>."
    )

    await message.answer_photo(
        photo=r['avatar_url'],
        caption=card_text,
        reply_markup=get_confirm_keyboard()
    )


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
    r = data.get('roblox', {})

    app_record = {
        "user_id": user.id,
        "username": user.username or "",
        "full_name": user.full_name or "",
        "name": data.get("name", user.first_name),
        "age": data.get("age", 0),
        "country": data.get("country", "Не указана"),
        "roblox_username": r.get("name", ""),
        "roblox_display_name": r.get("displayName", ""),
        "roblox_id": r.get("id", 0),
        "roblox_created": r.get("created_date", ""),
        "avatar_url": r.get("avatar_url", "")
    }

    PENDING_APPLICATIONS[user.id] = app_record
    save_pending_application(
        user_id=app_record["user_id"],
        username=app_record["username"],
        full_name=app_record["full_name"],
        name=app_record["name"],
        age=app_record["age"],
        country=app_record["country"],
        roblox_username=app_record["roblox_username"],
        roblox_display_name=app_record["roblox_display_name"],
        roblox_id=app_record["roblox_id"],
        roblox_created=app_record["roblox_created"],
        avatar_url=app_record["avatar_url"]
    )

    if user.username:
        tg_profile = f"@{user.username}"
    else:
        tg_profile = f'<a href="tg://user?id={user.id}">{html.escape(user.full_name)}</a>'

    admin_caption = (
        "📥 <b>Новая заявка в NEON BLUR!</b> 💖\n\n"
        f"👤 <b>Имя:</b> {html.escape(str(data.get('name')))}\n"
        f"🎂 <b>Возраст:</b> {data.get('age')}\n"
        f"🌍 <b>Страна:</b> {html.escape(str(data.get('country')))}\n"
        f"🔗 <b>Профиль TG:</b> {tg_profile}\n"
        f"🆔 <b>TG User ID:</b> <code>{user.id}</code>\n"
        f"🎮 <b>Roblox Ник:</b> <a href=\"{r.get('profile_url', '')}\">{html.escape(str(r.get('name', '')))}</a> (Display: {html.escape(str(r.get('displayName', '')))})\n"
        f"🆔 <b>Roblox ID:</b> <code>{r.get('id', '')}</code>\n"
        f"📅 <b>Регистрация в Roblox:</b> {r.get('created_date', '')}"
    )

    if not ADMIN_CHAT_ID:
        logger.error("ADMIN_CHAT_ID не настроен!")
        await callback.message.answer("❌ Ошибка настройки бота: не указан ADMIN_CHAT_ID.")
        await callback.answer()
        return

    try:
        await bot.send_photo(
            chat_id=ADMIN_CHAT_ID,
            photo=r.get('avatar_url', ''),
            caption=admin_caption,
            reply_markup=get_admin_keyboard(user.id)
        )
        await callback.message.answer("Ваша заявка отправлена на рассмотрение администраторам! ⏳")
        await state.clear()
        await callback.answer("Заявка отправлена!")

        log_text = (
            "📥 <b>[ЛОГ] Новая заявка отправлена в админ-чат</b>\n\n"
            f"👤 <b>Имя:</b> {html.escape(str(data.get('name')))}\n"
            f"🎂 <b>Возраст:</b> {data.get('age')}\n"
            f"🌍 <b>Страна:</b> {html.escape(str(data.get('country')))}\n"
            f"🔗 <b>TG:</b> {tg_profile} (<code>{user.id}</code>)\n"
            f"🎮 <b>Roblox:</b> <a href=\"{r.get('profile_url', '')}\">{html.escape(str(r.get('name', '')))}</a>\n"
            f"🆔 <b>Roblox ID:</b> <code>{r.get('id', '')}</code>\n"
            f"📅 <b>Дата регистрации:</b> {r.get('created_date', '')}"
        )
        await send_log(bot, log_text, photo=r.get('avatar_url', None))

    except Exception as e:
        logger.error(f"Ошибка при отправке заявки в админ-чат: {e}")
        await callback.message.answer("❌ Не удалось отправить заявку. Пожалуйста, попробуйте позже.")
        await callback.answer("Ошибка при отправке", show_alert=True)


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
            invite_link = await bot.create_chat_invite_link(
                chat_id=HOUSE_CHAT_ID,
                member_limit=1
            )

            app_data = PENDING_APPLICATIONS.get(applicant_id) or get_pending_application(applicant_id)
            if app_data:
                add_or_update_member(
                    user_id=app_data["user_id"],
                    username=app_data.get("username", ""),
                    full_name=app_data.get("full_name", ""),
                    name=app_data.get("name", "Участник"),
                    age=app_data.get("age", 0),
                    country=app_data.get("country", "Не указана"),
                    roblox_username=app_data.get("roblox_username", ""),
                    roblox_display_name=app_data.get("roblox_display_name", ""),
                    roblox_id=app_data.get("roblox_id", 0),
                    roblox_created=app_data.get("roblox_created", ""),
                    avatar_url=app_data.get("avatar_url", ""),
                    role="Участник"
                )

            kb = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="📱 Открыть NEON BLUR", web_app=WebAppInfo(url=WEBAPP_URL))]
                ]
            )
            await bot.send_message(
                chat_id=applicant_id,
                text=(
                    "Поздравляем! Твоя заявка в NEON BLUR одобрена! 🎉💖\n\n"
                    f"Вот твоя личная одноразовая ссылка для входа в хаус-чат: {invite_link.invite_link}\n\n"
                    "Твой скин и профиль уже добавлены в приложение хауса! 👇"
                ),
                reply_markup=kb
            )

            new_caption = (
                f"{original_caption}\n\n"
                f"✅ <b>Заявка принята</b> администратором {admin_mention}\n"
                f"💾 <i>Участник автоматически сохранен в базе и приложении!</i>"
            )
            await callback.message.edit_caption(caption=new_caption, reply_markup=None)
            await callback.answer("Заявка успешно принята!")

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
                "❌ Ошибка! Проверьте права бота в хаус-чате.",
                show_alert=True
            )

    elif action == "reject":
        try:
            await bot.send_message(
                chat_id=applicant_id,
                text="К сожалению, твоя заявка в хаус была отклонена. 😔"
            )

            new_caption = (
                f"{original_caption}\n\n"
                f"❌ <b>Заявка отклонена</b> администратором {admin_mention}"
            )
            await callback.message.edit_caption(caption=new_caption, reply_markup=None)
            await callback.answer("Заявка отклонена!")

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
                f"❌ <b>Заявка отклонена</b> администратором {admin_mention}"
            )
            await callback.message.edit_caption(caption=new_caption, reply_markup=None)
            await callback.answer("Заявка отклонена.")


# ================== КОМАНДЫ ДЛЯ АДМИНИСТРАТОРОВ ==================

@router.message(Command("add"))
async def cmd_add_member(message: Message):
    """
    Команда для администраторов: /add USER_ID ROBLOX_NICK [Имя] [Роль]
    """
    args = message.text.split(maxsplit=4)
    if len(args) < 3:
        await message.answer("⚠️ Использование: <code>/add USER_ID ROBLOX_NICK [Имя] [Роль]</code>\nПример: <code>/add 123456789 Builderman Назар Создатель</code>")
        return

    try:
        user_id = int(args[1])
    except ValueError:
        await message.answer("❌ USER_ID должен быть числом!")
        return

    roblox_nick = args[2]
    name = args[3] if len(args) > 3 else "Участник"
    role = args[4] if len(args) > 4 else "Участник"

    r = await get_roblox_user(roblox_nick)
    if not r:
        await message.answer(f"❌ Ник Roblox «{roblox_nick}» не найден!")
        return

    add_or_update_member(
        user_id=user_id,
        username="",
        full_name=name,
        name=name,
        age=0,
        country="Не указана",
        roblox_username=r["name"],
        roblox_display_name=r["displayName"],
        roblox_id=r["id"],
        roblox_created=r["created_date"],
        avatar_url=r["avatar_url"],
        role=role
    )
    await message.answer(f"✅ Участник <b>{html.escape(name)}</b> (Roblox: <code>{r['name']}</code>, Роль: <b>{role}</b>) успешно добавлен в базу и приложение!")


@router.message(Command("setrole"))
async def cmd_set_role(message: Message):
    """
    Команда для изменения роли: /setrole USER_ID РОЛЬ (Создатель / Администратор / Участник)
    """
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("⚠️ Использование: <code>/setrole USER_ID РОЛЬ</code>\nНапример: <code>/setrole 123456789 Создатель</code>")
        return

    try:
        user_id = int(args[1])
    except ValueError:
        await message.answer("❌ USER_ID должен быть числом!")
        return

    role = args[2].strip()
    if update_member_role(user_id, role):
        await message.answer(f"✅ Роль пользователя <code>{user_id}</code> обновлена на <b>«{html.escape(role)}»</b>!")
    else:
        await message.answer(f"❌ Пользователь <code>{user_id}</code> не найден в базе.")
