import logging

from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.types import  CallbackQuery
import random
from aiogram import Bot, Dispatcher
from aiogram.types import  Message
from aiogram.types import FSInputFile
from datetime import timedelta
import asyncio
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from datetime import datetime
from aiogram.types import WebAppInfo
from aiogram import Router, F, types
import os
from aiogram.client.session.aiohttp import AiohttpSession

# Пути к файлам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, 'Задания')


router = Router()


# Конфигурация
import logging
from aiogram import Bot, Dispatcher

# Конфигурация
BOT_TOKEN = "..."
ADMIN_IDS = [1824224788, 7066386368]
session = AiohttpSession(proxy='http://proxy.server:3128')
bot = Bot(token='...', session=session)

# Инициализация бота без прокси

dp = Dispatcher()


# Клавиатуры
kb_type1 = types.InlineKeyboardMarkup(inline_keyboard=[[
    types.InlineKeyboardButton(text="A", callback_data="ans_A"),
    types.InlineKeyboardButton(text="B", callback_data="ans_B"),
    types.InlineKeyboardButton(text="C", callback_data="ans_C"),
    types.InlineKeyboardButton(text="D", callback_data="ans_D")
]])

kb_type2 = types.InlineKeyboardMarkup(inline_keyboard=[[
    types.InlineKeyboardButton(text="A", callback_data="ans_A"),
    types.InlineKeyboardButton(text="B", callback_data="ans_B"),
    types.InlineKeyboardButton(text="C", callback_data="ans_C")
]])

kb_type3 = types.InlineKeyboardMarkup(inline_keyboard=[[
    types.InlineKeyboardButton(text="Правда", callback_data="ans_true"),
    types.InlineKeyboardButton(text="Ложь", callback_data="ans_false")
]])

main_kb = types.ReplyKeyboardMarkup(keyboard=[
    [types.KeyboardButton(text="👤 Профиль")],
    [types.KeyboardButton(text="📚 Задания")],
    [types.KeyboardButton(text="🌐 Наш сайт", web_app=WebAppInfo(url="https://vk.link/punctle"))]
], resize_keyboard=True)

admin_kb = types.InlineKeyboardMarkup(inline_keyboard=[
    [types.InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
    [types.InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")],
    [types.InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users")],
])

# Справочные материалы
reference = {
    'ssp': """📝 ССП - Сложносочинённые предложения

• Части равноправны по смыслу
• Соединяются сочинительными союзами: И, А, НО, ИЛИ, ЛИБО, ДА (в значении НО)
• Перед союзами ставится запятая

✏️ Пример: Солнце светило ярко, и птицы пели в саду.""",

    'spp': """📝 СПП - Сложноподчинённые предложения

• Состоят из главной и придаточной части
• Придаточная часть присоединяется подчинительными союзами: ЧТО, ЧТОБЫ, ПОТОМУ ЧТО, ЕСЛИ, КОГДА, КОТОРЫЙ, ГДЕ, КУДА
• Запятая ставится на границе главной и придаточной частей

✏️ Пример: Я знаю (главная часть), что завтра будет дождь (придаточная часть)

📌 Особенности СПП:
• Придаточная часть начинается с союзов или союзных слов
• Главная часть - это основное предложение

3 вида подчинения:
1. Последовательное - одна придаточная подчиняется другой
2. Параллельное - придаточные одинаково подчиняются главной
3. Однородное - придаточные равноправны между собой""",

    'bsp': """📝 БСП - Бессоюзные сложные предложения

• Части соединяются без союзов
• Знаки препинания зависят от смысловых отношений

📌 Знаки препинания:

Запятая (,) ставится:
• При перечислении действий или явлений
✏️ Пример: Светит солнце, поют птицы, шумят деревья.

Двоеточие (:) ставится:
• Если вторая часть поясняет первую
• Если вторая часть указывает причину
✏️ Пример: Я не пошёл гулять: на улице шёл дождь.

Тире (-) ставится:
• Если вторая часть содержит следствие, результат
• При противопоставлении
• При быстрой смене событий
✏️ Пример: Сверкнула молния - раздался гром."""
}


# Хранилища данных
users = {}
user_tasks = {}
user_completion = {}
subscribed_users = set()
notification_tasks = {}
unlimited_users = set()
user_streaks = {}
user_last_tasks = {}
TESTER_IDS = set()

dp = Dispatcher()


sticker_id = 'CAACAgIAAxkBAAEOaXRn__lNwJ0qXBvl1z_wO8F0dZZSSgACiW0AAl1kAUjRgGfXDULIzzYE'

# Основные команды
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    users[user_id] = {
        "username": message.from_user.username or "Пользователь",
        "reg_date": datetime.now().strftime("%d.%m.%Y"),
        "tasks_completed": 0,
        "last_active": datetime.now().strftime("%d.%m.%Y")
    }

    await message.reply_sticker(sticker_id)
    await message.answer(
        "Добро пожаловать в бот для изучения пунктуации! 📚\n"
        "Используйте меню для навигации.",
        reply_markup=main_kb
    )


@dp.message(Command('help'))
async def help_command(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="ССП", callback_data="show_ssp"),
            InlineKeyboardButton(text="СПП", callback_data="show_spp"),
            InlineKeyboardButton(text="БСП", callback_data="show_bsp")
        ],
        [InlineKeyboardButton(text="Полный справочник", callback_data="show_full")]
    ])

    help_text = """
Этот бот поможет вам с пунктуацией в русском языке.

Создатели бота: @Kr1stal1ty, @giepei
Редактор бота: @L3thalL0v3
Дизайнер стикеров: @QwertYnG0
Тестировщики: @lxnofg, @real1st9

Поддержать проект: 2200700409709424
Т-банк"""


    await message.answer(help_text, reply_markup=kb)

@dp.callback_query(F.data.startswith("show_"))
async def process_show_callback(callback: CallbackQuery):
    section = callback.data.split("_")[1]

    if section == "full":
        full_text = (
            f"{reference['ssp']}\n\n"
            f"{reference['spp']}\n\n"
            f"{reference['bsp']}"
        )
        await callback.message.edit_text(full_text, reply_markup=get_back_kb())
    else:
        await show_section(callback.message, section)

    await callback.answer()
async def show_section(message: Message, section: str):
    if section in reference:
        await message.edit_text(
            reference[section],
            reply_markup=get_back_kb()
        )
def get_back_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="ССП", callback_data="show_ssp"),
            InlineKeyboardButton(text="СПП", callback_data="show_spp"),
            InlineKeyboardButton(text="БСП", callback_data="show_bsp")
        ],
        [InlineKeyboardButton(text="Полный справочник", callback_data="show_full")]
    ])







@dp.message(lambda m: m.text == "📚 Задания")
async def start_tasks(message: types.Message):
    user_id = message.from_user.id
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Проверяем, выполнял ли пользователь задания сегодня
    if user_id in user_last_tasks:
        last_task_date = user_last_tasks[user_id]
        if last_task_date == current_date:
            await message.answer(
                "⏳ На сегодня лимит заданий исчерпан.\n"
                "Новые задания будут доступны завтра в 00:00!"
            )
            return

    # Если пользователь еще не выполнял задания сегодня
    random_tasks = random.sample(BD, 3)
    user_tasks[user_id] = {
        'tasks': random_tasks,
        'current': 0,
        'correct': 0
    }
    user_last_tasks[user_id] = current_date

    await message.answer(
        "🎯 Начинаем тестирование!\n"
        "⚠️ Напоминаем: доступно только 3 задания в день."
    )
    await send_task(user_id, random_tasks[0])
async def reset_daily_limits():
    while True:
        now = datetime.now()
        # Ждем до следующего дня 00:00
        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        await asyncio.sleep((tomorrow - now).total_seconds())
        # Сбрасываем ограничения
        user_last_tasks.clear()
        logging.info("Daily task limits have been reset")
async def send_task(user_id: int, task: dict):
    try:
        if task['type'] in ['type1', 'type2', 'type3']:
            keyboard = task.get('keyboard', None)
            await bot.send_photo(
                user_id,
                FSInputFile(task['image']),
                reply_markup=keyboard
            )
        elif task['type'] == 'type4':
            await bot.send_photo(user_id, FSInputFile(task['image']))
            await bot.send_message(user_id, task['instruction'])
    except Exception as e:
        logging.error(f"Ошибка отправки задания {task['id']}: {e}")
        await bot.send_message(user_id, "Произошла ошибка при отправке задания.")






# Стикеры по категориям
STICKERS = {
    'perfect': [
        'CAACAgIAAxkBAAEOYvxn_r8PX1S_ApSJ_TfrLUPbvQfwOQACS34AAlKQ-EtkjVo7I27D9zYE',  # радость
        'CAACAgIAAxkBAAEOYwRn_r8TJaNKxZ8akoEfnUJSAbzM9QACX24AAn8h-EvNmTP3VhXccjYE',  # победа
        'CAACAgIAAxkBAAEOYv5n_r8QpzVaU2A4vcwbMCfynFOJoAAC4XUAAq7r-UsxWMpRengxODYE'  # супер
    ],
    'good': [
        'CAACAgIAAxkBAAEOaWhn__lH72qhs7rORswnCMWkNea3RwACzGcAAo3xAAFIfHe3DjDnR3o2BA',  # молодец
        'CAACAgIAAxkBAAEOaWxn__lJpTpMtfqkmxNlyZHPz7sjVwACZ3MAAhNGAAFIRiKuI6MpTY82BA',  # хорошо
        'CAACAgIAAxkBAAEOaWZn__lGJ22NUhjRt6jE1kbMl6WQigACn2sAAg3IAUgqhIYKrIPMMDYE'  # неплохо
    ],
    'wrong': [
        'CAACAgIAAxkBAAEOYwZn_r8UJ44Lm__qDvZgHDU9G6ZMFAACyXkAAgLt8EsUYcIk5V3hETYE',  # ошибка
        'CAACAgIAAxkBAAEOYwJn_r8SKR0Cqs0M2cDCXOtaHNP1OgACZHMAAgaP-EubryFGiNRBHDYE',  # подумай
        'CAACAgIAAxkBAAEOaXBn__lMGm9dajgaAk0iahJNdSdxqwACmXEAAr4AAQFI2oiiDmKHvqg2BA'  # неверно
    ]
}
# Сообщения для разных результатов
MESSAGES = {
    'perfect': [
        "🌟 Блестяще! Продолжай в том же духе!",
        "✨ Превосходно! Ты на верном пути!",
        "🎯 Идеально! Так держать!"
    ],
    'good': [
        "👍 Хороший результат!",
        "💪 Отличная работа!",
        "😊 Молодец!"
    ],
    'wrong': [
        "📚 Не переживай, в следующий раз получится лучше!",
        "🎯 Практика ведет к совершенству!",
        "💡 Учимся на ошибках!"
    ]
}

@dp.callback_query(lambda c: c.data.startswith("ans_"))
async def check_answer(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = user_tasks[user_id]
    task = user['tasks'][user['current']]
    answer = callback.data.split("_")[1]  # Получаем ответ пользователя

    # Добавим отладочную информацию
    logging.info(f"User answer: {answer}, Correct answer: {task['correct']}, Task ID: {task['id']}")

    # Приводим оба значения к одному регистру для сравнения
    is_correct = answer.upper() == task['correct'].upper()
    user['correct'] += 1 if is_correct else 0

    # Определяем категорию стикера
    if is_correct:
        sticker_category = 'perfect' if user['correct'] > 2 else 'good'
    else:
        sticker_category = 'wrong'

    # Отправляем стикер
    await callback.message.answer_sticker(
        random.choice(STICKERS[sticker_category])
    )

    # Отправляем сообщение с результатом
    if is_correct:
        await callback.message.answer(random.choice(MESSAGES[sticker_category]))
    else:
        await callback.message.answer(
            f"{random.choice(MESSAGES['wrong'])}\n\n"
            f"📝 Пояснение:\n{task['explanation']}\n\n"
            f"✨ Правильный ответ: {task['correct']}"
        )

    # Убираем кнопки из предыдущего сообщения
    await callback.message.edit_reply_markup(reply_markup=None)

    # Переходим к следующему заданию или показываем результаты
    user['current'] += 1
    if user['current'] < len(user['tasks']):
        await asyncio.sleep(2)
        await send_task(user_id, user['tasks'][user['current']])
    else:
        await show_results(user_id, callback.message)
# В функции show_results добавьте обновление статистики
async def show_results(user_id: int, message: types.Message):
    user = user_tasks[user_id]
    correct = user['correct']
    total = len(user['tasks'])

    # Обновляем статистику
    users[user_id]["tasks_completed"] += correct
    users[user_id]["last_active"] = datetime.now().strftime("%d.%m.%Y")

    # Определяем категорию результата
    if correct == total:
        category = 'perfect'
        user_streaks[user_id] = user_streaks.get(user_id, 0) + 1
        result = f"""🎉 Великолепный результат!
📊 Счет: {correct}/{total}
🔥 Стрик: {user_streaks[user_id]} дней подряд"""
    elif correct >= total * 0.7:
        category = 'good'
        result = f"""👍 Хороший результат!
📊 Счет: {correct}/{total}"""
    else:
        category = 'wrong'
        result = f"""📚 Есть куда расти!
📊 Счет: {correct}/{total}"""

    # Отправляем стикер
    await message.answer_sticker(random.choice(STICKERS[category]))



    # Отправляем результат
    await message.answer(
        f"{result}\n\n"
        "⏳ Следующие задания будут доступны завтра в 00:00!"
    )

    # Добавляем мотивационное сообщение для отличного результата
    if category == 'perfect':
        await asyncio.sleep(1)
        await message.answer("🌟 Продолжай в том же духе! Ты делаешь большие успехи!")



# Обработчик кнопки профиля
@dp.message(lambda m: m.text == "👤 Профиль")
async def show_profile(message: types.Message):
    user_id = message.from_user.id

    # Проверяем, зарегистрирован ли пользователь
    if user_id not in users:
        users[user_id] = {
            "username": message.from_user.username or "Пользователь",
            "reg_date": datetime.now().strftime("%d.%m.%Y"),
            "tasks_completed": 0,
            "last_active": datetime.now().strftime("%d.%m.%Y")
        }
        await message.answer(
            "👋 Добро пожаловать! Я создал для вас профиль.\n"
            "Используйте /start для начала работы с ботом."
        )

    user = users[user_id]
    streak = user_streaks.get(user_id, 0)

    # Подсчет статистики
    total_tasks = user['tasks_completed']

    # Определяем уровень
    level, next_level = calculate_level(total_tasks)

    # Проверяем статус уведомлений
    notifications_status = "🔔 Включены" if user_id in subscribed_users else "🔕 Выключены"

    profile_text = f"""
👤 Профиль пользователя

📝 Имя: @{user['username']}
📅 Дата регистрации: {user['reg_date']}

📊 Статистика:
• Всего решено заданий: {total_tasks}
• Текущий стрик: {streak} дней 🔥

🏆 Достижения:
• Уровень: {level}
• До следующего уровня: {next_level - total_tasks} заданий

🔔 Уведомления: {notifications_status}
⏱️ Последняя активность: {user['last_active']}
"""

    # Создаем клавиатуру
    notification_text = "🔕 Выключить уведомления" if user_id in subscribed_users else "🔔 Включить уведомления"

    profile_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="📊 Рейтинг", callback_data="leaderboard")],
        [types.InlineKeyboardButton(text=notification_text, callback_data="toggle_notifications")]
    ])

    try:
        await message.answer(profile_text, reply_markup=profile_kb)
    except Exception as e:
        logging.error(f"Ошибка при отображении профиля: {e}")
        await message.answer(
            "Произошла ошибка при загрузке профиля. "
            "Попробуйте использовать /start для перезапуска бота."
        )

# Обработчик рейтинга
@dp.callback_query(lambda c: c.data == "leaderboard")
async def show_leaderboard(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    sorted_users = sorted(
        users.items(),
        key=lambda x: x[1]['tasks_completed'],
        reverse=True
    )[:10]

    leaderboard_text = "🏆 Топ-10 пользователей:\n\n"
    for i, (user_id, user_data) in enumerate(sorted_users, 1):
        leaderboard_text += f"{i}. @{user_data['username']} - {user_data['tasks_completed']} заданий\n"

    notification_text = "🔕 Выключить уведомления" if user_id in subscribed_users else "🔔 Включить уведомления"
    back_kb = types.InlineKeyboardMarkup(inline_keyboard=[
    [types.InlineKeyboardButton(text=notification_text, callback_data="toggle_notifications")],
    [types.InlineKeyboardButton(text="◀️ Назад к профилю", callback_data="back_to_profile")]
    ])

    await callback.message.edit_text(leaderboard_text, reply_markup=back_kb)

# Обработчик переключения уведомлений
@dp.callback_query(lambda c: c.data == "toggle_notifications")
async def toggle_notifications(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if user_id in subscribed_users:
        subscribed_users.discard(user_id)
        if user_id in notification_tasks:
            notification_tasks[user_id].cancel()
        notification_status = "🔕 Уведомления выключены"
    else:
        subscribed_users.add(user_id)
        await schedule_next_notification(user_id)
        notification_status = "🔔 Уведомления включены"

    await callback.answer(notification_status)

    # Обновляем текущее сообщение
    if callback.message.text.startswith("👤 Профиль"):
        await back_to_profile(callback)
    elif callback.message.text.startswith("🏆 Топ"):
        await show_leaderboard(callback)

# Обработчик кнопки возврата к профилю
@dp.callback_query(lambda c: c.data == "back_to_profile")
async def back_to_profile(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    user = users[user_id]
    streak = user_streaks.get(user_id, 0)

    # Подсчет статистики
    total_tasks = user['tasks_completed']

    # Определяем уровень
    level, next_level = calculate_level(total_tasks)

    # Проверяем статус уведомлений
    notifications_status = "🔔 Включены" if user_id in subscribed_users else "🔕 Выключены"

    profile_text = f"""
👤 Профиль пользователя

📝 Имя: @{user['username']}
📅 Дата регистрации: {user['reg_date']}

📊 Статистика:
• Всего решено заданий: {total_tasks}
• Текущий стрик: {streak} дней 🔥

🏆 Достижения:
• Уровень: {level}
• До следующего уровня: {next_level - total_tasks} заданий

🔔 Уведомления: {notifications_status}
⏱️ Последняя активность: {user['last_active']}
"""

    # Создаем клавиатуру
    notification_text = "🔕 Выключить уведомления" if user_id in subscribed_users else "🔔 Включить уведомления"

    profile_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="📊 Рейтинг", callback_data="leaderboard")],
        [types.InlineKeyboardButton(text=notification_text, callback_data="toggle_notifications")]
    ])

    await callback.message.edit_text(profile_text, reply_markup=profile_kb)

# Вспомогательные функции
def calculate_level(tasks):
    """Рассчитывает текущий уровень пользователя"""
    if tasks >= 100:
        return "Эксперт 🎓", 999
    elif tasks >= 50:
        return "Знаток 📚", 100
    elif tasks >= 25:
        return "Студент 📖", 50
    elif tasks >= 10:
        return "Ученик 📝", 25
    else:
        return "Новичок 🔰", 10

def get_rank(accuracy):
    """Определяет ранг пользователя на основе точности"""
    if accuracy >= 95:
        return "🏆 Легенда"
    elif accuracy >= 90:
        return "💎 Профессионал"
    elif accuracy >= 80:
        return "🥇 Продвинутый"
    elif accuracy >= 70:
        return "🥈 Опытный"
    elif accuracy >= 60:
        return "🥉 Практик"
    else:
        return "🎯 Начинающий"

# Функции для уведомлений
async def schedule_next_notification(user_id: int):
    """Планирует следующее уведомление"""
    now = datetime.now()
    next_notification = now.replace(hour=6, minute=0, second=0)
    if now.hour >= 6:
        next_notification += timedelta(days=1)

    delay = (next_notification - now).total_seconds()
    task = asyncio.create_task(send_notification(user_id, delay))
    notification_tasks[user_id] = task

async def send_notification(user_id: int, delay: float):
    """Отправляет уведомление"""
    try:
        await asyncio.sleep(delay)
        await bot.send_message(user_id, "🎯 Доступны новые задания!")
        await schedule_next_notification(user_id)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logging.error(f"Ошибка отправки уведомления {user_id}: {e}")







# Админ-функции
@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    await message.answer("👨‍💼 Панель администратора:", reply_markup=admin_kb)

@dp.callback_query(lambda c: c.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return

    total_users = len(users)
    active_users = len([u for u in users.values() if u['last_active'] == datetime.now().strftime("%d.%m.%Y")])
    total_tasks = sum(u['tasks_completed'] for u in users.values())

    stats_text = f"""
📊 Статистика бота:

👥 Всего пользователей: {total_users}
✅ Активных сегодня: {active_users}
📚 Выполнено заданий: {total_tasks}
🔔 Подписано на уведомления: {len(subscribed_users)}
    """
    await callback.message.edit_text(stats_text)

@dp.callback_query(lambda c: c.data == "admin_broadcast")
async def admin_broadcast(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return

    await callback.message.edit_text(
        "📢 Введите текст для рассылки:\n"
        "Отправьте сообщение в формате:\n"
        "/send Ваш текст"
    )

@dp.message(Command("send"))
async def send_broadcast(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    broadcast_text = message.text.replace("/send ", "")
    successful = 0
    failed = 0

    for user_id in users:
        try:
            await bot.send_message(user_id, broadcast_text)
            successful += 1
        except Exception as e:
            failed += 1
            logging.error(f"Ошибка отправки сообщения {user_id}: {e}")

    await message.answer(
        f"📢 Рассылка завершена:\n"
        f"✅ Успешно: {successful}\n"
        f"❌ Не доставлено: {failed}"
    )

@dp.callback_query(lambda c: c.data == "admin_users")
async def admin_users(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS:
        return

    users_text = "👥 Активные пользователи:\n\n"
    for user_id, data in users.items():
        users_text += (
            f"ID: {user_id}\n"
            f"Username: @{data['username']}\n"
            f"Рег.: {data['reg_date']}\n"
            f"Заданий: {data['tasks_completed']}\n"
            f"Стрик: {user_streaks.get(user_id, 0)}\n"
            f"Активность: {data['last_active']}\n\n"
        )

    # Разбиваем на части если текст длинный
    if len(users_text) > 4096:
        for x in range(0, len(users_text), 4096):
            chunk = users_text[x:x + 4096]
            await callback.message.answer(chunk)
    else:
        await callback.message.edit_text(users_text)



# Обновите функцию start_tasks для учета тестировщиков
@dp.message(lambda m: m.text == "📚 Задания")
async def start_tasks(message: types.Message):
    user_id = message.from_user.id
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Проверяем, является ли пользователь тестировщиком
    if user_id not in TESTER_IDS:
        # Проверяем лимит для обычных пользователей
        if user_id in user_last_tasks:
            last_task_date = user_last_tasks[user_id]
            if last_task_date == current_date:
                await message.answer(
                    "⏳ На сегодня лимит заданий исчерпан.\n"
                    "Новые задания будут доступны завтра в 00:00!"
                )
                return

    # Генерируем задания
    random_tasks = random.sample(BD, 3)
    user_tasks[user_id] = {
        'tasks': random_tasks,
        'current': 0,
        'correct': 0
    }

    # Обновляем дату последнего выполнения только для обычных пользователей
    if user_id not in TESTER_IDS:
        user_last_tasks[user_id] = current_date
        await message.answer(
            "🎯 Начинаем тестирование!\n"
            "⚠️ Напоминаем: доступно только 3 задания в день."
        )
    else:
        await message.answer("🎯 Начинаем тестирование!")

    await send_task(user_id, random_tasks[0])





# База данных заданий
BD = [
    # Задания типа 1 (A, B, C, D)
    {
        'id' : 1,
        'image': r'/home/KrE3st/bot/Задания/Задания 1/1.1.png',
        'correct': 'A',
        'type': 'type1',
        'keyboard': kb_type1,
        'explanation': '''Предложение сложное, состоит из 5 частей, каждую часть отделяем запятой.
Сделаем схему предложения:
(1 хотя...), [2 ...], (3 что...), (4 что), и (5 что).
Однородными являются предложения 3 и 5 (казалось что?). Но к 3-ему присоединено своё придаточное (4-е), последовательным подчинением, и его, четвертое, нужно закрыть запятой. Вот откуда перед «и» берётся запятая. Если бы четвертого предложения не было, и запятой бы между однородными не было. «Выбросьте» его и проверьте.
Запятые должны стоять на местах 1, 2, 3 и 4.'''
    },
    {
        'id' : 2,
        'image': r'/home/KrE3st/bot/Задания/Задания 1/1.2.png',
        'correct': 'B',
        'type': 'type1',
        'keyboard': kb_type1,
        'explanation': '''Запятая 1 отделяет части сложносочиненного предложения.
Запятые 3 и 4 выделяют придаточное предложение «чтобы ощутить их нежную бархатистость».
Запятые должны стоять на местах 1, 3 и 4.'''
    },
    {
        'id' : 3,
        'image': r'/home/KrE3st/bot/Задания/Задания 1/1.3.png',
        'correct': 'D',
        'type': 'type1',
        'keyboard': kb_type1,
        'explanation': '''Приведем верное написание.
[Даша заметила], (что, (когда вслед за звонком в столовой появлялся Рощин), Катя сразу не поворачивала к нему головы, а минуточку медлила.)
Запятые 1, 2, 3 обозначают границы придаточных в СПП; зпт 4 для однородных сказуемых.
Ответ: 1234'''
    },
    {
        'id' : 4,
        'image': r'/home/KrE3st/bot/Задания/Задания 1/1.4.png',
        'correct': 'A',
        'type': 'type1',
        'keyboard': kb_type1,
        'explanation': '''Приведем верное написание.
[С Кузнецкого моста я заехал в кондитерскую на Тверской и, (хотя желал притвориться), нет второй части(что меня в кондитерской преимущественно интересуют газеты), не смог удержаться от нескольких сладких пирожков].
Запятые под номерами 2, 3, 4 выделяют придаточные предложения.
Запятые должны стоять на местах 2, 3 и 4.'''
    },
    {
        'id' : 5,
        'image': r'/home/KrE3st/bot/Задания/Задания 1/1.5.png',
        'correct': 'B',
        'type': 'type1',
        'keyboard': kb_type1,
        'explanation': '''Приведем верное написание.
Они заговорили о здоровье графини и об общих знакомых, (1) и, (2) когда прошли те требуемые приличием десять минут, (3) после которых гость может встать, (4) Николай поднялся и стал прощаться.
Запятая под номером 1 отделяет части сложного предложения, соединенные союзом И, запятые под номерами 2, 3, 4 выделяют придаточные предложения.
Запятые должны стоять на местах 1, 2, 3 и 4.'''
    },
    {
        'id' : 6,
        'image': r'/home/KrE3st/bot/Задания/Задания 1/1.6.png',
        'correct': 'D',
        'type': 'type1',
        'keyboard': kb_type1,
        'explanation': '''Расставим запятые.
Стояла жара, (1) и, (2) если вдруг налетал ветерок (3) и приносил с собой прохладу, (4) деревья благодарно кивали ветвями.
Запятая под номером 1 отделяет основы: «стояла жара» и «деревья кивали»; запятые под номерами 2 и 4 выделяют придаточное предложение «если вдруг налетал ветерок и приносил с собой прохладу».
Запятые должны стоять на местах 1, 2 и 4.'''
    },

    # Задания типа 2 (А, Б, В)
    {
        'id' : 7,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.1.png',
        'correct': 'B',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''Если пойдёт дождь, мы останемся дома, а если будет солнечно, пойдём гулять.
Здесь две придаточные части равноправны и соединены союзом «а». Они обе отвечают на один и тот же вопрос главного предложения («Что произойдёт, если...»), имеют одинаковую грамматическую форму и структуру — значит, подчинение параллельное.
'''
    },
    {
        'id' : 8,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.2.png',
        'correct': 'C',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''Я знаю, что он приедет, и что привезёт подарок.
Первое придаточное («что он приедет») относится к главному предложению, второе («что привезёт подарок») зависит от первого придаточного. Подчинительные отношения идут последовательно одно за другим.
'''
    },
    {
        'id' : 9,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.3.png',
        'correct': 'B',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''Я думаю, что он сдаст экзамен, потому что хорошо подготовился.
Придаточные части («что он сдаст экзамен», «потому что хорошо подготовился») зависят от одного и того же главного предложения и находятся в отношениях причины и следствия, оба отвечают на вопросы одного типа («Почему я так думаю?»). Это именно однородное подчинение.
'''
    },
    {
        'id' : 10,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.4.png',
        'correct': 'A',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''
        Последовательное подчинение подразумевает зависимость второй придаточной части от первой.'''
    },
    {
        'id' : 11,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.5.png',
        'correct': 'C',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''Он сказал, что сдаст экзамен и что будет поступать в университет.
Здесь второе придаточное («что будет поступать в университет») связано с первым («что сдаст экзамен»), а само первое связано с главным («он сказал»). Получилась цепочка подчинения, то есть последовательное подчинение.
'''
    },
    {
        'id' : 12,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.6.png',
        'correct': 'B',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''Эти придаточные относятся к главному предложению («Мы пошли в парк») независимо друг от друга и не выстраиваются в цепочку, где одно придаточное зависело бы от другого. Соответственно, придаточные части соединяются параллельно.
        '''
    },
    # Задания типа 3 (Правда/Ложь)

# Добавьте остальные задания по аналогии
    ]
def validate_task(task):
    required_fields = ['id', 'image', 'correct', 'type', 'keyboard', 'explanation']
    for field in required_fields:
        if field not in task:
            return False, f"Missing field: {field}"

    # Проверка соответствия типа и клавиатуры
    keyboard_mapping = {
        'type1': kb_type1,
        'type2': kb_type2,
        'type3': kb_type3
    }

    if task['type'] in keyboard_mapping:
        if task['keyboard'] != keyboard_mapping[task['type']]:
            return False, f"Keyboard mismatch for type {task['type']}"

    # Проверка формата правильного ответа
    valid_answers = {
        'type1': ['A', 'B', 'C', 'D'],
        'type2': ['A', 'B', 'C'],
        'type3': ['true', 'false']
    }

    if task['type'] in valid_answers:
        if task['correct'].upper() not in [ans.upper() for ans in valid_answers[task['type']]]:
            return False, f"Invalid correct answer format: {task['correct']}"

    return True, "Task is valid"

# Проверка всей базы данных
def validate_database():
    for task in BD:
        is_valid, message = validate_task(task)
        if not is_valid:
            logging.error(f"Task {task['id']}: {message}")
            return False
    return True





async def main():
    try:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='bot.log'  # Логирование в файл
        )

        # Регистрация роутера
        dp.include_router(router)

        # Запускаем задачу сброса ограничений
        asyncio.create_task(reset_daily_limits())

        # Запускаем уведомления для подписанных пользователей
        for user_id in subscribed_users:
            await schedule_next_notification(user_id)

        # Запуск бота
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logging.error(f"Critical error: {e}")
        raise





if __name__ == "__main__":
    asyncio.run(main())
