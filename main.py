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
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# Пути к файлам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, 'Задания')


router = Router()


# Конфигурация
import logging
from aiogram import Bot, Dispatcher

# Конфигурация
BOT_TOKEN = "7378923438:AAE65rxUVcyFr30iV1nEpBhh7nHDy7gonUg"
ADMIN_IDS = [1824224788, 7066386368]
session = AiohttpSession(proxy='http://proxy.server:3128')
bot = Bot(token='7378923438:AAE65rxUVcyFr30iV1nEpBhh7nHDy7gonUg', session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

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
    [types.KeyboardButton(text="📖 Теория"), types.KeyboardButton(text="📚 Задания")],
    [types.KeyboardButton(text="🌐 Наш сайт", web_app=WebAppInfo(url="https://vk.link/punctle")), types.KeyboardButton(text="👤 Профиль")]
], resize_keyboard=True)
admin_kb = types.InlineKeyboardMarkup(inline_keyboard=[
    [types.InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
    [types.InlineKeyboardButton(text="📢 Рассылка", callback_data="admin_broadcast")],
    [types.InlineKeyboardButton(text="👥 Пользователи", callback_data="admin_users")],
])

# Справочные материалы
reference = {
    'ssp': """📝 <b>ССП - Сложносочинённые предложения</b>
• Части равноправны по смыслу
• Соединяются сочинительными союзами: <i>И</i>, <i>А</i>, <i>НО</i>, <i>ИЛИ</i>, <i>ЛИБО</i>, <i>ДА</i> (в значении <i>НО</i>)
• Перед союзами ставится запятая

<b><i>Пример:</i></b> <i>Солнце светило ярко, и птицы пели в саду.</i>

<b>Правила знаков препинания в ССП:</b>
1. Точка с запятой ставится, если части значительно распространены.
   <b><i>Пример:</i></b> <i>"Одни, меньшая часть, признавали князя Андрея чем-то особенным от себя и от всех других людей; и с этими людьми князь Андрей был прост и приятен."</i>

2. Тире ставится, если вторая часть содержит неожиданный результат или резкое противопоставление.
   <b><i>Пример:</i></b> <i>"Но мой кошелёк истощился - и нет моих милых друзей."</i>

3. Запятая не ставится, если простые предложения имеют общий второстепенный элемент.
   <b><i>Пример:</i></b> <i>"Но слишком рано твой ударил час и вещее перо из рук упало."</i>
""",

    'spp': """📝 <b>СПП - Сложноподчинённые предложения</b>
• Состоят из главной и придаточной части
• Придаточная часть присоединяется подчинительными союзами: <i>ЧТО</i>, <i>ЧТОБЫ</i>, <i>ПОТОМУ ЧТО</i>, <i>ЕСЛИ</i>, <i>КОГДА</i>, <i>КОТОРЫЙ</i>, <i>ГДЕ</i>, <i>КУДА</i>
• Запятая ставится на границе главной и придаточной частей

<b><i>Пример:</i></b> <i>Я знаю (главная часть), что завтра будет дождь (придаточная часть).</i>

<b>Особенности СПП:</b>
• Придаточная часть начинается с союзов или союзных слов
• Главная часть - это основное предложение

<b>3 вида подчинения:</b>
1. Последовательное - одна придаточная подчиняется другой
2. Параллельное - придаточные одинаково подчиняются главной
3. Однородное - придаточные равноправны между собой""",

    'bsp': """📝 <b>БСП - Бессоюзные сложные предложения</b>
• Части соединяются без союзов
• Знаки препинания зависят от смысловых отношений

<b>Знаки препинания:</b>

<i>Запятая (_) ставится:</i>
• При перечислении действий или явлений
<b><i>Пример:</i></b> <i>Светит солнце, поют птицы, шумят деревья.</i>

<i>Двоеточие (:) ставится:</i>
• Если вторая часть поясняет первую
• Если вторая часть указывает причину
<b><i>Пример:</i></b> <i>Я не пошёл гулять: на улице шёл дождь.</i>

<i>Тире (-) ставится:</i>
• Если вторая часть содержит следствие, результат
• При противопоставлении
• При быстрой смене событий
<b><i>Пример:</i></b> <i>Сверкнула молния - раздался гром.</i>
"""
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
    help_text = """
Этот бот поможет вам с пунктуацией в русском языке.

Создатели бота: @Kr1stal1ty, @giepei
Редактор бота: @L3thalL0v3
Дизайнер стикеров: @QwertYnG0
Тестировщики: @lxnofg, @real1st9

Поддержать проект: 2200700409709424
Т-банк"""


    await message.answer(help_text)



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
            InlineKeyboardButton(text="ССП", callback_data="show_ssp", parse_mode=ParseMode.HTML),
            InlineKeyboardButton(text="СПП", callback_data="show_spp", parse_mode=ParseMode.HTML),
            InlineKeyboardButton(text="БСП", callback_data="show_bsp", parse_mode=ParseMode.HTML)
        ],
        [InlineKeyboardButton(text="Полный справочник", callback_data="show_full", parse_mode=ParseMode.HTML)]
    ])



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






@dp.message(lambda m: m.text == "📖 Теория")
async def show_theory(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="ССП", callback_data="show_ssp", parse_mode=ParseMode.HTML),
            InlineKeyboardButton(text="СПП", callback_data="show_spp", parse_mode=ParseMode.HTML),
            InlineKeyboardButton(text="БСП", callback_data="show_bsp", parse_mode=ParseMode.HTML)
        ],
        [InlineKeyboardButton(text="Полный справочник", callback_data="show_full", parse_mode=ParseMode.HTML)]
    ])

    await message.answer("📚 Теория", reply_markup=kb)



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
                "Новые задания будут доступны завтра с 00:00!"
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
@dp.message()
async def handle_text_answer(message: types.Message):
    user_id = message.from_user.id

    # Проверяем, есть ли у пользователя активное задание
    if user_id not in user_tasks:
        return

    user = user_tasks[user_id]
    if user['current'] >= len(user['tasks']):
        return

    current_task = user['tasks'][user['current']]

    # Проверяем, является ли текущее задание типом 4
    if current_task['type'] != 'type4':
        return

    # Проверяем ответ (удаляем пробелы и приводим к верхнему регистру)
    user_answer = ''.join(message.text.strip().split())
    correct_answer = ''.join(current_task['correct'].strip().split())
    is_correct = user_answer == correct_answer

    if is_correct:
        user['correct'] += 1
        sticker_category = 'perfect' if user['correct'] > 2 else 'good'
        # Отправляем стикер и сообщение об успехе
        await message.answer_sticker(random.choice(STICKERS[sticker_category]))
        await message.answer(random.choice(MESSAGES[sticker_category]))
    else:
        # Отправляем стикер и объяснение ошибки
        await message.answer_sticker(random.choice(STICKERS['wrong']))
        await message.answer(
            f"{random.choice(MESSAGES['wrong'])}\n\n"
            f"📝 Пояснение:\n{current_task['explanation']}\n\n"
            f"✨ Правильный ответ: {current_task['correct']}"
        )

    # Переходим к следующему заданию или показываем результаты
    user['current'] += 1
    if user['current'] < len(user['tasks']):
        await asyncio.sleep(2)
        await send_task(user_id, user['tasks'][user['current']])
    else:
        await show_results(user_id, message)


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
    {
        'id' : 13,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.1.png',
        'correct': 'true',
        'type': 'type3',
        'keyboard': kb_type3,
        'explanation': '''Части сложносочинённого предложения (ССП) равноправны, и между ними действительно можно поставить точку, если они выражают законченную мысль и могут существовать как отдельные предложения.
        '''
    },
    {
        'id' : 14,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.2.png',
        'correct': 'true',
        'type': 'type3',
        'keyboard': kb_type3,
        'explanation': '''В сложноподчинённом предложении (СПП) может быть последовательное подчинение придаточных. Это значит, что одно придаточное подчиняется главному, а другое — первому придаточному, и так далее — выстраивается "цепочка" подчинения.
        '''
    },
    {
        'id' : 15,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.3.png',
        'correct': 'false',
        'type': 'type3',
        'keyboard': kb_type3,
        'explanation': '''В сложноподчинённом предложении (СПП) может быть последовательное подчинение придаточных. Это значит, что одно придаточное подчиняется главному, а другое — первому придаточному, и так далее — выстраивается "цепочка" подчинения.
        '''
    },
    {
        'id' : 16,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.4.png',
        'correct': 'false',
        'type': 'type3',
        'keyboard': kb_type3,
        'explanation': '''В сложноподчинённом предложении главная часть может стоять как до, так и после придаточной.
        '''
    },
    {
        'id' : 17,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.5.png',
        'correct': 'true',
        'type': 'type3',
        'keyboard': kb_type3,
        'explanation': '''Утверждение «Придаточные части в сложноподчинённом предложении могут быть однородными» — верно.
        '''
    },
    {
        'id' : 18,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.6.png',
        'correct': 'true',
        'type': 'type3',
        'keyboard': kb_type3,
        'explanation': '''Утверждение «В бессоюзном сложном предложении нет союзов, связывающих части» — верно.
        '''
    },
    # Задания типа 4 (ЕГЭ)
    {
        'id' : 19,
        'image': r'/home/KrE3st/bot/Задания/Задания 4/4.1.png',
        'correct': '1234',
        'type': 'type4',
        'instruction': 'Напишите ответ цифрами в порядке возрастания',
        'explanation': '''На месте цифры 1 ставится запятая, потому что она выделяет придаточное уступки (хотя предъявлять договор он не обязан), стоящее перед главным предложением бывают ситуации.

На месте цифры 2 запятая ставится, так как она также отделяет придаточное определительное (когда это лучше сделать) от главного.

На месте цифры 3 ставится запятая, отделяющая придаточное цели (чтобы не портить отношения с людьми) от предыдущего придаточного.

На месте цифры 4 ставится запятая, отделяющая определительное придаточное (расположение которых впоследствии ещё может пригодиться) от предыдущего придаточного.

На месте цифр 5 и 6 запятые не ставятся, так как союзное слово которых оттянуто в середину придаточной части (отсутствие запятых легко обосновать, если заменить местоимение которых на соответствующее ему имя существительное из главной части предложения: людей).
        '''
    },
    {
        'id' : 20,
        'image': r'/home/KrE3st/bot/Задания/Задания 4/4.2.png',
        'correct': '125',
        'type': 'type4',
        'instruction': 'Напишите ответ цифрами в порядке возрастания',
        'explanation': '''На месте цифр 1, 2 и 5 ставятся запятые, потому что они обозначают границы придаточных предложений.

На месте цифр 3 и 4 запятые не ставятся, так как союзное слово который оттянуто в середину придаточной части (отсутствие запятых легко обосновать, если заменить местоимение который на соответствующее ему имя существительное из главной части предложения: разговор).
        '''
    },
    {
        'id': 21,
        'image': r'/home/KrE3st/bot/Задания/Задания 4/4.3.png',
        'correct': '1457',
        'type': 'type4',
        'instruction': 'Напишите ответ цифрами в порядке возрастания',
        'explanation': '''На месте цифры 1 ставится запятая, отделяющая определительное придаточное (владельцы которого мало что заслужили, кроме худой о себе славы по округе) от главного. При этом не ставятся запятые на месте цифр 2, 3: союзное слово которого оттянуто в середину придаточной части, отсутствие запятых легко обосновать, если заменить местоимение которого на соответствующее ему имя существительное из главной части предложения: поместья.

На месте цифры 4 ставится запятая, отделяющая первое придаточное определительное от второго, присоединяемого к предыдущему с помощью союзного слова где.

На месте цифры 5 ставится запятая, отделяющая придаточное определительное от придаточного уступки несмотря на то что никто уже даже не мог сказать. При этом запятая на месте цифры 6 не ставится: составной союз несмотря на то что может быть двояко оформлен с точки зрения пунктуации (возможна запятая перед частью этого союза (что), а не перед всем союзом целиком), но в данном примере цифра (6) стоит не перед, а после что, постановка запятой на месте этой цифры отделила бы средство связи (подчинительный союз) от самого предложения (грамматической основы).

Запятая на месте цифры 7 ставится, отделяя придаточное уступки от придаточного изъяснительного из-за чего именно появилась такая ненависть. Запятая на месте цифры 8 не ставится: постановка запятой на месте этой цифры отделила бы средство связи (союзное слово (из-за) чего) от самого предложения (грамматической основы).
        '''
    },
    {
        'id': 22,
        'image': r'/home/KrE3st/bot/Задания/Задания 4/4.4.png',
        'correct': '125',
        'type': 'type4',
        'instruction': 'Напишите ответ цифрами в порядке возрастания',
        'explanation': '''На месте цифры 1 ставится запятая, потому что что – это изъяснительный подчинительный союз, присоединяющий придаточное предложение к главному.

На месте цифр 2, 5 запятые ставятся, так как они выделяют придаточное определительное (под звуки которого совершалось шествие), разрывая им придаточное изъяснительное (что и торжественную песнь оргáна он воспроизвёл бы теперь без ошибки).

При этом не ставятся запятые 3, 4: союзное слово которого оттянуто в середину придаточной части, отсутствие запятых легко обосновать, если заменить местоимение которого на соответствующее ему имя существительное из главной части предложения: звуки оргáна.'''
    },
    {
        'id': 24,
        'image': r'/home/KrE3st/bot/Задания/Задания 4/4.5.png',
        'correct': '1347',
        'type': 'type4',
        'instruction': 'Напишите ответ цифрами в порядке возрастания',
        'explanation': '''На месте цифр 1 и 3 ставятся запятые, потому что они выделяют придаточную часть который учёные назвали «браслетом дружбы», разрывающую главную часть [Прибор... сможет достаточно ярко выразить эмоции и чувства вашего партнёра].

На месте цифры 2 запятая не ставится, так как союзное слово который в придаточной части является прямым дополнением и не требует обособления (отсутствие запятой легко обосновать, если заменить местоимение который на соответствующее ему имя существительное из главной части предложения: прибор).

Запятая на месте цифры 4 ставится, поскольку она отделяет новое придаточное определительное под действием которых браслет у вас на запястье будет нагреваться, изгибаться и вибрировать от главного предложения.

На месте цифр 5 и 6 запятые не ставятся, так как союзное слово которых оттянуто в середину придаточной части (отсутствие запятых легко обосновать, если заменить местоимение которых на соответствующие ему имена существительные из главной части предложения: эмоции и чувства).

Запятая на месте цифры 7 ставится, так как отделяет новое придаточное так что обладатель такого устройства с помощью специальных датчиков почувствует даже самое лёгкое прикосновение от предыдущего.
        '''
    },
    {
        'id': 23,
        'image': r'/home/KrE3st/bot/Задания/Задания 4/4.6.png',
        'correct': '1456',
        'type': 'type4',
        'instruction': 'Напишите ответ цифрами в порядке возрастания',
        'explanation': '''На месте цифры 1 ставится запятая, потому что она отделяет главное предложение от придаточной части в продолжение которых он пытался заставить себя решиться на проверку… и одновременно уговорить докторов.

На месте цифр 2 и 3 запятые не ставятся, так как союзное слово которых оттянуто в середину придаточной части (отсутствие запятых легко обосновать, если заменить местоимение которых на соответствующее ему имя существительное из главной части предложения: недель).

Запятые на месте цифр 4, 5 ставятся, поскольку они выделяют новое придаточное предложение что ему давалось с огромным трудом.

Запятая на месте цифры 6 ставится, поскольку она выделяет ещё одно придаточное предложение что здоров и ни в какой проверке не нуждается.
        '''
    },
    {
        'id': 24,
        'image': r'/home/KrE3st/bot/Задания/Задания 1/1.7.png',
        'correct': 'C',
        'type': 'type1',
        'keyboard': kb_type1,
        'explanation': '''Запятые под номерами 2, 4 выделяют однородные придаточные предложения 2 и 3. Они отвечают на один вопрос и относятся к главному 1: направился когда?

Запятые должны стоять на местах 2, 4.
        '''
    },
    {
        'id': 25,
        'image': r'/home/KrE3st/bot/Задания/Задания 4/4.7.png',
        'correct': '23',
        'type': 'type4',
        'instruction': 'Напишите ответ цифрами в порядке возрастания',
        'explanation': '''На месте цифры 1 не ставится запятая, потому что как только – это подчинительный союз времени, присоединяющий придаточное предложение к главному.

На месте цифры 2 запятая ставится, так как она отделяет придаточное обстоятельственное времени (как только Кудиныч увидел медведя) от главного.

На месте цифры 3 ставится запятая, отделяющая определительное придаточное (в нескольких шагах от которой расположена была деревня) от главного. При этом не ставятся запятые на месте цифр 4 и 5: союзное слово (от)которой оттянуто в середину придаточной части, отсутствие запятых легко обосновать, если заменить местоимение (от) которой на соответствующее ему имя существительное из главной части предложения: (от) опушки.
        '''
    },
    {
        'id': 26,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.7.png',
        'correct': 'C',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''Придаточные отвечают на один и тот же вопрос («какие?») и относятся к одному и тому же слову в главной части («дни»).
        '''
    },
{
        'id': 27,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.8.png',
        'correct': 'C',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''Оба придаточных относятся к одному главному предложению.
        '''
    },
{
        'id': 28,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.9.png',
        'correct': 'C',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''Придаточные связаны с главным предложением и отвечают на один и тот же вопрос («чему?»).
        '''
    },
{
        'id': 29,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.10.png',
        'correct': 'C',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''Придаточные связаны с главным предложением и связаны сочинительными союзами либо бессоюзно.
        '''
    },
{
        'id' : 30,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.7.png',
        'correct': 'true',
        'type': 'type3',
        'keyboard': kb_type3,
        'explanation': '''Это объясняется их равноправностью: простые предложения в составе сложного возможно разделить на простые, смысл их не потеряется.
        '''
    },
{
        'id' : 31,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.8.png',
        'correct': 'true',
        'type': 'type3',
        'keyboard': kb_type3,
    },
{
        'id' : 32,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.9.png',
        'correct': 'true',
        'type': 'type3',
        'keyboard': kb_type3,
        'explanation': '''Этим БСП отличаются от сложносочинённых и сложноподчинённых предложений, в которых данную роль выполняют союзы.
        '''
    },
{
        'id' : 33,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.10.png',
        'correct': 'true',
        'type': 'type3',
        'keyboard': kb_type3,
        'explanation': '''Тире следует поставить в том случае, если вторая часть сложносочинённого предложения содержит в себе результат, следствие либо резко противопоставлена первой части.
        '''
    },
{
        'id': 34,
        'image': r'/home/KrE3st/bot/Задания/Задания 1/1.8.png',
        'correct': 'A',
        'type': 'type1',
        'keyboard': kb_type1,
        'explanation': '''Запятая под номером 1 отделяет части, связанные сочинительной связью: «Рита сильно расстроилась из-за отъезда отца» и « но ... девочка быстро утешилась и перестала плакать». Запятые под номерами 2 и 3 выделяют придаточное предложение «когда он пообещал привезти ей из плавания настоящего большого попугая». Запятые под номерами 3 и 4 выделяют придаточное предложение «какого они видели недавно в зоопарке».

Запятые должны стоять на местах 1, 2, 3 и 4.
        '''
    },
{
        'id': 35,
        'image': r'/home/KrE3st/bot/Задания/Задания 1/1.9.png',
        'correct': 'D',
        'type': 'type1',
        'keyboard': kb_type1,
        'explanation': '''Запятая под номером 1 отделяет части, связанные подчинительной связью: «Илья Андреевич понимал» и «что (2) если не собрать яблоки до наступления холодов». Запятая под номером 3 отделяет части, связанные подчинительной связью: «(2) если не собрать яблоки до наступления холодов» и «то весь урожай погибнет», запятая под номером 4 отделяет части, связанные сочинительной связью: «Илья Андреевич понимал» и «но обстоятельства не позволяли ему оставить работу и уехать в деревню даже на несколько дней».

Ответ:134
        '''
    },
{
        'id': 36,
        'image': r'/home/KrE3st/bot/Задания/Задания 1/1.10.png',
        'correct': 'B',
        'type': 'type1',
        'keyboard': kb_type1,
        'explanation': '''На стыке союзов или союзов и союзных слов (и хотя, но когда, и если; что когда, что куда, который если и др.) запятая ставится тогда, когда после придаточной части нет союза но или второй части двойного союза  — то или так. Это как раз наш случай.

Запятые должны стоять на местах 1, 2, 3 и 4.
        '''
    },
    {
        'id': 37,
        'image': r'/home/KrE3st/bot/Задания/Задания 4/4.7.png',
        'correct': '23',
        'type': 'type4',
        'instruction': 'Напишите ответ цифрами в порядке возрастания',
        'explanation': '''На месте цифры 1 не ставится запятая, потому что как только – это подчинительный союз времени, присоединяющий придаточное предложение к главному.

На месте цифры 2 запятая ставится, так как она отделяет придаточное обстоятельственное времени (как только Кудиныч увидел медведя) от главного.

На месте цифры 3 ставится запятая, отделяющая определительное придаточное (в нескольких шагах от которой расположена была деревня) от главного.

При этом не ставятся запятые на месте цифр 4 и 5: союзное слово (от)которой оттянуто в середину придаточной части, отсутствие запятых легко обосновать, если заменить местоимение (от) которой на соответствующее ему имя существительное из главной части предложения: (от) опушки.'''
    },
    {
        'id': 38,
        'image': r'/home/KrE3st/bot/Задания/Задания 4/4.8.png',
        'correct': '145',
        'type': 'type4',
        'instruction': 'Напишите ответ цифрами в порядке возрастания',
        'explanation': '''Запятая на месте цифры  ставится, так как начинается придаточная часть при звуках трескучего голоса которого Артём… даже остановил работу. Союзное слово который в этой придаточной оттянуто в середину предложения (границы придаточной части легко определить, если заменить относительное местоимение который на соответствующее ему существительное господин из предыдущей части). Запятые на месте цифр  и  не ставятся.
Запятые на месте  и  ставятся, так как они выделяют ещё одну придаточную часть чтобы посмеяться всласть, которая находится внутри предыдущей придаточной.'''
    },
{
        'id': 39,
        'image': r'/home/KrE3st/bot/Задания/Задания 4/4.9.png',
        'correct': '1256',
        'type': 'type4',
        'instruction': 'Напишите ответ цифрами в порядке возрастания',
        'explanation': '''Запятая на месте цифры 1 ставится, так как здесь заканчивается первая придаточная часть (сколько лет ни проходило бы между нашими встречами с Володькой) и начинается главная (он оставался всё тем же улыбчивым толстячком).
Запятая на месте цифры 2 ставится, так как начинается новая придаточная часть с оттянутым в середину союзным словом который: оптимизма и добродушия у которого с годами становилось только больше (границы придаточной части легко увидеть, если заменить относительное местоимение который на соответствующее ему существительное толстячок из главной части). Соответственно, запятые на месте цифр 3 и 4 не ставятся.
Запятые на месте цифр 5 и 6 ставятся, так как они выделяют ещё одну придаточную часть (несмотря на то что на его долю выпало немало трудностей), которая находится внутри другой придаточной (это можно проверить, опустив эту придаточную).'''
    },
{
        'id': 40,
        'image': r'/home/KrE3st/bot/Задания/Задания 4/4.10.png',
        'correct': '125',
        'type': 'type4',
        'instruction': 'Напишите ответ цифрами в порядке возрастания',
        'explanation': '''На месте цифры 1 ставится запятая, отделяющая придаточное предложение с союзом как от главного предложения.

На месте цифры 2 запятая ставится перед придаточным определительным. Союзное слово «которой» стоит не в начале, а в середине придаточного определительного предложения, поэтому запятая ставится не перед словом «которой», а перед словом «сын».

На месте цифры 3 запятая ставится перед придаточным предложением с союзом когда.'''
    },
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
