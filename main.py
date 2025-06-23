import logging

from aiogram import Bot, Dispatcher
from datetime import timedelta
import asyncio
import random
import json
from datetime import datetime
from aiogram.types import WebAppInfo
from aiogram.types import CallbackQuery
from aiogram.types import Message
from aiogram.types import FSInputFile
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram import Router, types
import os
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from typing import Dict
import time
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    waiting_broadcast_text = State()
    waiting_for_ban_id = State()
    waiting_for_unban_id = State()


rate_limits: Dict[str, Dict[str, float]] = {}

users = {}
user_tasks = {}
subscribed_users = set()
user_streaks = {}
user_last_tasks = {}
user_completed_tasks = {}  # {user_id: set(task_ids)}
last_notification_time = {}  # {user_id: datetime}
user_training_data = {}
user_training_state = {}
banned_users = set()
last_streak_time = {}  # {user_id: datetime}
user_next_notification = {}  # Словарь для хранения времени следующего уведомления

# Пути к файлам
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(BASE_DIR, 'Задания')
DATA_FILE = os.path.join(BASE_DIR, 'user_data.json')
RATING_FILE = os.path.join(BASE_DIR, 'rating_data.json')

router = Router()

# Конфигурация
BOT_TOKEN = "7378923438:AAE65rxUVcyFr30iV1nEpBhh7nHDy7gonUg"
ADMIN_IDS = [1824224788]
session = AiohttpSession(proxy='http://proxy.server:3128')
bot = Bot(token='7378923438:AAE65rxUVcyFr30iV1nEpBhh7nHDy7gonUg', session=session,
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))

dp = Dispatcher()

# Клавиатуры
kb_type1 = types.InlineKeyboardMarkup(inline_keyboard=[
    [
        types.InlineKeyboardButton(text="A", callback_data="ans_A"),
        types.InlineKeyboardButton(text="B", callback_data="ans_B"),
        types.InlineKeyboardButton(text="C", callback_data="ans_C"),
        types.InlineKeyboardButton(text="D", callback_data="ans_D")
    ],
    [types.InlineKeyboardButton(text="Теория", callback_data="show_theory")]
])
kb_type2 = types.InlineKeyboardMarkup(inline_keyboard=[
    [
        types.InlineKeyboardButton(text="A", callback_data="ans_A"),
        types.InlineKeyboardButton(text="B", callback_data="ans_B"),
        types.InlineKeyboardButton(text="C", callback_data="ans_C")
    ],
    [types.InlineKeyboardButton(text="Теория", callback_data="show_theory")]
])
kb_type3 = types.InlineKeyboardMarkup(inline_keyboard=[
    [
        types.InlineKeyboardButton(text="Правда", callback_data="ans_true"),
        types.InlineKeyboardButton(text="Ложь", callback_data="ans_false")
    ],
    [types.InlineKeyboardButton(text="Теория", callback_data="show_theory")]
])
main_kb = types.ReplyKeyboardMarkup(keyboard=[
    [types.KeyboardButton(text="📖 Теория"), types.KeyboardButton(text="📚 Задания")],
    [types.KeyboardButton(text="✍️ Тренировка")],
    [types.KeyboardButton(text="👤 Профиль"), types.KeyboardButton(text="🏆 Рейтинг")],
    [types.KeyboardButton(text="🌐 Сайт", web_app=WebAppInfo(url="https://vk.link/punctle")),
     types.KeyboardButton(text="🌐 VK", web_app=WebAppInfo(url="https://vk.com/punctle")),
    ]
], resize_keyboard=True)
admin_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
    [InlineKeyboardButton(text="📋 Логи", callback_data="admin_logs")],
])
training_kb = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text="➡️ Следующее задание", callback_data="next_training"),
        InlineKeyboardButton(text="🔚 Закончить", callback_data="end_training")
    ]
])
sticker_id = 'CAACAgIAAxkBAAEOaXRn__lNwJ0qXBvl1z_wO8F0dZZSSgACiW0AAl1kAUjRgGfXDULIzzYE'


@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id

    # Добавляем пользователя в подписчики
    subscribed_users.add(user_id)

    if user_id not in users:
        users[user_id] = {
            "username": message.from_user.username or "Пользователь",
            "reg_date": datetime.now().strftime("%d.%m.%Y"),
            "tasks_completed": 0,
            "last_active": datetime.now().strftime("%d.%m.%Y"),
            "total_answers": 0,
            "correct_answers": 0,
            "best_streak": 0
        }
        save_rating_data()

    await message.reply_sticker(sticker_id)
    await message.answer(
        "Добро пожаловать в бот для изучения пунктуации! 📚\n"
        "Используйте меню для навигации.",
        reply_markup=main_kb
    )

@dp.message(Command("creators"))
async def authors_handler(message: Message):
    authors_text = """
👥 Авторы проекта "Бот для изучения пунктуации":

🔧 Создатели:
- @Kr1stal1ty — разработчик, ответственный за функционал и логику работы бота.
- @giepei — идейный вдохновитель, вносящий идеи и улучшения.

📝 Редактор:
- @L3thalL0v3 — редактор, следящий за качеством и актуальностью учебных материалов.

🎨 Дизайнер:
- @QwertYnG0 — дизайнер, создающий визуальные элементы, делающие взаимодействие с ботом более увлекательным.

🧪 Тестировщики:
- @lxnofg — тестировщик, проверяющий работоспособность и удобство использования бота.
- @real1st9 — тестировщик, занимающийся улучшением пользовательского опыта и обратной связью.

💖 Поддержите проект:
Ваши пожертвования помогут в развитии и улучшении бота.
2200700409709424
Т-банк

📩 Обратная связь:
Мы всегда открыты для ваших предложений и замечаний!

👤 Пользователи:
Каждый пользователь — важная часть нашего сообщества. Вы помогаете нам становиться лучше, и ваша активность вдохновляет нас на новые идеи!
"""

    await message.answer(authors_text)

@dp.message(lambda m: m.text == "📝 Обратная связь")
async def feedback_handler(message: Message):
    await message.answer(
        "По всем вопросам обращайтесь к @L3thalL0v3"
    )

@dp.message(lambda m: m.text == "📖 Теория")
async def show_theory(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="ССП", callback_data="show_ssp"),
            InlineKeyboardButton(text="СПП", callback_data="show_spp"),
            InlineKeyboardButton(text="БСП", callback_data="show_bsp")
        ]
    ])
    await message.answer("📚 Выберите раздел теории:", reply_markup=kb)
@dp.callback_query(lambda c: c.data == "show_theory")
async def process_show_theory(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="ССП", callback_data="show_ssp"),
            types.InlineKeyboardButton(text="СПП", callback_data="show_spp"),
            types.InlineKeyboardButton(text="БСП", callback_data="show_bsp")
        ]
    ])
    await callback.message.answer("Выберите раздел теории:", reply_markup=kb)
    await callback.answer()

@dp.message(lambda m: m.text == "👤 Профиль")
async def show_profile(message: types.Message):
    user_id = message.from_user.id

    if user_id not in users:
        users[user_id] = {
            "username": message.from_user.username or "Пользователь",
            "reg_date": datetime.now().strftime("%d.%m.%Y"),
            "tasks_completed": 0,
            "last_active": datetime.now().strftime("%d.%m.%Y"),
            "total_answers": 0,
            "correct_answers": 0,
            "best_streak": 0
        }

    user = users[user_id]
    total_tasks = user['tasks_completed']
    current_streak = user_streaks.get(user_id, 0)

    # Определяем ранг пользователя
    rank = "🌱 Новичок"
    if total_tasks >= 100:
        rank = "🎓 Мастер"
    elif total_tasks >= 50:
        rank = "⭐️ Продвинутый"
    elif total_tasks >= 20:
        rank = "📚 Ученик"

    # Вычисляем прогресс
    next_rank_tasks = 20
    if total_tasks >= 100:
        progress = 100
    elif total_tasks >= 50:
        next_rank_tasks = 100 - total_tasks
        progress = (total_tasks - 50) * 2
    elif total_tasks >= 20:
        next_rank_tasks = 50 - total_tasks
        progress = (total_tasks - 20) * 3.3
    else:
        next_rank_tasks = 20 - total_tasks
        progress = total_tasks * 5

    # Создаем прогресс-бар
    progress_bar_length = 10
    filled_length = int(progress_bar_length * progress / 100)
    progress_bar = "■" * filled_length + "▢" * (progress_bar_length - filled_length)

    # Обновляем лучшую серию если текущая больше
    best_streak = user.get('best_streak', 0)
    if current_streak > best_streak:
        user['best_streak'] = current_streak
        best_streak = current_streak

    # Вычисляем точность
    total_answers = user.get('total_answers', 0)
    correct_answers = user.get('correct_answers', 0)
    accuracy = (correct_answers / total_answers * 100) if total_answers > 0 else 0

    profile_text = (
        f"👤 *Профиль пользователя*\n\n"
        f"*Основная информация:*\n"
        f"📝 Имя: @{user['username']}\n"
        f"📅 Дата регистрации: {user['reg_date']}\n"
        f"🏆 Ранг: {rank}\n\n"

        f"*Статистика:*\n"
        f"✅ Решено заданий: {total_tasks}\n"
        f"📈 Точность: {accuracy:.1f}%\n"
        f"🔥 Текущая серия: {current_streak}\n"
        f"⭐️ Лучшая серия: {best_streak}\n"
        f"⏱️ Последняя активность: {user['last_active']}\n\n"

        f"*Прогресс до следующего ранга:*\n"
        f"{progress_bar} {progress:.1f}%\n"
        f"Осталось решить: {next_rank_tasks} заданий"
    )

    try:
        await message.answer(
            profile_text,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logging.error(f"Ошибка при отображении профиля: {e}")
        await message.answer(
            "Произошла ошибка при загрузке профиля. "
            "Попробуйте использовать /start для перезапуска бота."
        )

@dp.message(lambda m: m.text == "📚 Задания")
async def start_tasks(message: types.Message):
    user_id = message.from_user.id
    current_time = datetime.now()

    if user_id in user_last_tasks:
        last_task_time = datetime.strptime(user_last_tasks[user_id], "%Y-%m-%d %H:%M:%S")
        time_diff = current_time - last_task_time

        if time_diff < timedelta(hours=6):
            remaining_time = timedelta(hours=6) - time_diff
            hours = remaining_time.seconds // 3600
            minutes = (remaining_time.seconds % 3600) // 60

            time_message = ""
            if hours > 0:
                time_message += f"{hours} час(ов) "
            if minutes > 0:
                time_message += f"{minutes} минут"

            await message.answer(
                f"⏳ Следующие задания будут доступны через {time_message}!"
            )
            return

    available_tasks = get_available_tasks(user_id)

    if len(available_tasks) >= 3:
        random_tasks = random.sample(available_tasks, 3)
    else:
        random_tasks = available_tasks

    user_tasks[user_id] = {
        'tasks': random_tasks,
        'current': 0,
        'correct': 0
    }

    if user_id not in user_completed_tasks:
        user_completed_tasks[user_id] = set()
    for task in random_tasks:
        user_completed_tasks[user_id].add(task['id'])

    user_last_tasks[user_id] = current_time.strftime("%Y-%m-%d %H:%M:%S")

    # Добавляем эти строки для уведомлений
    next_notification_time = current_time + timedelta(hours=6)
    user_next_notification[user_id] = next_notification_time

    # Сохраняем данные
    save_rating_data()

    await message.answer(
        "🎯 Начинаем тестирование!\n"
        "⚠️ Напоминаем: следующие задания будут доступны через 6 часов."
    )
    await send_task(user_id, random_tasks[0])

@dp.message(lambda m: m.text == "✍️ Тренировка")
async def start_training(message: types.Message):
    user_id = message.from_user.id
    # Устанавливаем состояние тренировки
    user_training_state[user_id] = {'is_training': True}
    # Выбираем случайное предложение
    sentence = random.choice(training_sentences)
    # Сохраняем текущее предложение для пользователя
    user_training_data[user_id] = sentence

    await message.answer(
        "Перепишите предложение, расставляя знаки препинания:\n\n"
        f"{sentence['sentence']}"
    )

@dp.message(lambda m: m.text == "🏆 Рейтинг")
async def show_rating(message: types.Message):
    try:
        # Создаем список пользователей с их статистикой
        user_stats = []
        for user_id, user_data in users.items():
            user_stats.append({
                'username': user_data['username'],
                'tasks_completed': user_data['tasks_completed'],
                'streak': user_streaks.get(user_id, 0)
            })

        # Сортируем по количеству решенных заданий
        user_stats.sort(key=lambda x: (x['tasks_completed'], x['streak']), reverse=True)

        # Формируем текст рейтинга
        rating_text = "🏆 Рейтинг пользователей:\n\n"

        # Добавляем топ-10 пользователей
        for i, user in enumerate(user_stats[:10], 1):
            # Добавляем медали для первых трех мест
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "•")

            # Формируем строку рейтинга
            rating_line = f"{medal} {i}. @{user['username']}\n"
            rating_line += f"📚 Решено заданий: {user['tasks_completed']}\n"
            if user['streak'] > 0:
                rating_line += f"🔥 Серия: {user['streak']}\n"
            rating_line += "\n"

            rating_text += rating_line

        # Добавляем позицию текущего пользователя, если он не в топ-10
        current_user_id = message.from_user.id
        current_user_position = next((i for i, user in enumerate(user_stats, 1)
                                      if user['username'] == users[current_user_id]['username']), None)

        if current_user_position > 10:
            rating_text += "\nВаша позиция:\n"
            user_data = users[current_user_id]
            rating_text += f"• {current_user_position}. @{user_data['username']}\n"
            rating_text += f"📚 Решено заданий: {user_data['tasks_completed']}\n"
            if user_streaks.get(current_user_id, 0) > 0:
                rating_text += f"🔥 Серия: {user_streaks[current_user_id]}\n"

        await message.answer(rating_text)

    except Exception as e:
        logging.error(f"Error showing rating: {e}")
        await message.answer("Произошла ошибка при показе рейтинга. Попробуйте позже.")

@dp.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMIN_IDS:
        return

    await message.answer(
        "👨‍💻 Панель администратора\n\n"
        "Выберите действие:",
        reply_markup=admin_kb
    )


# Клавиатура для ССП
def get_ssp_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Что такое ССП", callback_data="ssp_main")],
        [InlineKeyboardButton(text="🔄 Союзы в ССП", callback_data="ssp_unions")],
        [InlineKeyboardButton(text="❗️ Знаки препинания", callback_data="ssp_punctuation")],
        [InlineKeyboardButton(text="📚 Примеры с разбором", callback_data="ssp_examples")],
        [InlineKeyboardButton(text="◀️ Назад к разделам", callback_data="show_theory")]
    ])
ssp_theory = {
    'main': """<b>Что такое сложносочинённое предложение (ССП)?</b>

Сложносочинённое предложение - это такое предложение, части которого равноправны по смыслу и соединены сочинительными союзами.

<b>Главные признаки ССП:</b>

1. РАВНОПРАВНОСТЬ ЧАСТЕЙ:
• Обе части самостоятельны
• Каждую часть можно сделать отдельным предложением
• Части не зависят друг от друга
• Между частями можно поставить точку

2. СОЧИНИТЕЛЬНЫЕ СОЮЗЫ:
• Всегда стоят между частями
• Показывают связь между частями
• Перед союзами обычно ставится запятая

<b>Как найти части ССП?</b>
• В каждой части есть своя грамматическая основа
• Между частями стоит сочинительный союз
• Каждая часть может стать отдельным предложением

Пример:
Солнце светило ярко, и птицы пели в саду.
• 1 часть: [Солнце светило ярко]
• 2 часть: [птицы пели в саду]
• Союз: И
• Можно разделить: Солнце светило ярко. Птицы пели в саду.""",

    'unions': """<b>Сочинительные союзы в ССП</b>

В ССП используются три группы союзов:

1. <b>СОЕДИНИТЕЛЬНЫЕ СОЮЗЫ</b>
Показывают, что действия происходят одновременно или следуют друг за другом.

• И
Пример: Солнце светило, и птицы пели.
(действия происходят одновременно)

• ДА (в значении И)
Пример: Солнце светило, да ветер дул.
(действия происходят одновременно)

• НИ...НИ
Пример: Ни солнце не светило, ни птицы не пели.
(отрицание нескольких действий)

• ТОЖЕ, ТАКЖЕ
Пример: Солнце светило, также дул лёгкий ветерок.
(добавление похожего действия)

2. <b>ПРОТИВИТЕЛЬНЫЕ СОЮЗЫ</b>
Показывают, что действия противопоставляются или не соответствуют ожиданиям.

• А
Пример: Солнце светило, а дождь шёл.
(противопоставление)

• НО
Пример: Солнце светило, но было холодно.
(противоречие)

• ДА (в значении НО)
Пример: Хотел прийти, да не смог.
(противоречие)

• ОДНАКО
Пример: Было холодно, однако мы пошли гулять.
(уступка)

• ЗАТО
Пример: Погода испортилась, зато настроение улучшилось.
(возмещение)

3. <b>РАЗДЕЛИТЕЛЬНЫЕ СОЮЗЫ</b>
Показывают, что действия чередуются или исключают друг друга.

• ИЛИ
Пример: То солнце светит, или дождь идёт.
(чередование)

• ЛИБО
Пример: Либо ты идёшь со мной, либо остаёшься дома.
(выбор одного из двух)

• ТО...ТО
Пример: То солнце светит, то тучи находят.
(чередование)

• НЕ ТО...НЕ ТО
Пример: Не то дождь шёл, не то снег падал.
(неуверенность в определении)""",

    'punctuation': """<b>Знаки препинания в ССП</b>

1. <b>ЗАПЯТАЯ СТАВИТСЯ:</b>

🔹 Перед всеми сочинительными союзами:
• Дождь прошёл, и выглянуло солнце.
• Солнце светило, но было холодно.
• Гремит гром, или сверкает молния.

🔹 При повторяющихся союзах:
• И гром гремит, и молния сверкает.
• То дождь шёл, то солнце светило.
• Ни ветра нет, ни солнца нет.

2. <b>ЗАПЯТАЯ НЕ СТАВИТСЯ:</b>

🔹 Если есть общий второстепенный член:
• Сегодня светит солнце и дует ветер.
(общее слово "сегодня" относится к обеим частям)

🔹 Если есть общее придаточное предложение:
• Когда пришла весна, зацвели цветы и прилетели птицы.
(общее придаточное "когда пришла весна")

🔹 Если есть общее вводное слово:
• Возможно, завтра пойдёт дождь и будет гроза.
(общее вводное слово "возможно")

3. <b>ТИРЕ СТАВИТСЯ:</b>

🔹 При резком противопоставлении:
• Пришла весна — и всё расцвело.

🔹 При неожиданном результате:
• Сверкнула молния — и грянул гром.

4. <b>ТОЧКА С ЗАПЯТОЙ ставится:</b>

🔹 Если части сильно распространены:
• Солнце медленно опускалось за горизонт, окрашивая небо в розовые тона; птицы постепенно затихали, готовясь к ночному отдыху.""",

    'examples': """<b>Разбор ССП на примерах</b>

1. <b>С соединительным союзом И:</b>
"Солнце светило ярко, и птицы пели в саду"

Разбор:
• 1 часть: [Солнце светило ярко]
• 2 часть: [птицы пели в саду]
• Союз: И (соединительный)
• Запятая перед И
• Действия происходят одновременно

2. <b>С противительным союзом НО:</b>
"Дождь закончился, но лужи остались"

Разбор:
• 1 часть: [Дождь закончился]
• 2 часть: [лужи остались]
• Союз: НО (противительный)
• Запятая перед НО
• Действия противоречат ожиданиям

3. <b>С разделительным союзом ТО...ТО:</b>
"То солнце выглянет, то снова туча набежит"

Разбор:
• 1 часть: [солнце выглянет]
• 2 часть: [снова туча набежит]
• Союз: ТО...ТО (разделительный)
• Запятая между частями
• Действия чередуются

4. <b>Без запятой (общий второстепенный член):</b>
"Сегодня светит солнце и дует ветер"

Разбор:
• 1 часть: [светит солнце]
• 2 часть: [дует ветер]
• Союз: И
• Общее слово: СЕГОДНЯ
• Запятая не нужна

5. <b>С тире (неожиданный результат):</b>
"Сверкнула молния — и грянул гром"

Разбор:
• 1 часть: [Сверкнула молния]
• 2 часть: [грянул гром]
• Союз: И
• Тире показывает быструю смену событий"""
}

# Клавиатура для СПП
def get_spp_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Что такое СПП", callback_data="spp_main")],
        [InlineKeyboardButton(text="🔄 Виды придаточных", callback_data="spp_types")],
        [InlineKeyboardButton(text="❗️ Знаки препинания", callback_data="spp_punctuation")],  # Новая кнопка
        [InlineKeyboardButton(text="📚 Виды подчинения", callback_data="spp_structure")],
        [InlineKeyboardButton(text="📋 Примеры с разбором", callback_data="spp_examples")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_theory")]
    ])
spp_theory = {
    'main': """<b>Что такое сложноподчинённое предложение (СПП)?</b>

Простыми словами: это сложное предложение, где одна часть (главная) подчиняет себе другую часть (придаточную).

<b>Как узнать СПП?</b>
1. Смотрим на союзы:
• ЧТО, ЧТОБЫ, ЕСЛИ, КОГДА, ПОТОМУ ЧТО → скорее всего это СПП
• Союзные слова: КОТОРЫЙ, ГДЕ, КУДА, ОТКУДА → тоже признак СПП

2. Задаём вопрос от главной части к придаточной:
• Что делает? Какой? Где? Когда? Почему? → если можем задать вопрос, это СПП

<b>Примеры:</b>
🔹 Я знаю (главное), что завтра будет дождь (придаточное).
• Вопрос: что я знаю?
• Союз: ЧТО

🔹 Когда пришла весна (придаточное), птицы вернулись (главное).
• Вопрос: когда вернулись?
• Союз: КОГДА

<b>Важно помнить:</b>
• Главная часть может стоять в начале, в середине или в конце
• Придаточная часть всегда зависит от главной
• Придаточных частей может быть несколько""",

    'types': """<b>Виды придаточных предложений в СПП</b>

1. <b>Изъяснительные (отвечают на вопросы что? о чём?)</b>
• Союзы: ЧТО, ЧТОБЫ, КАК
Пример: Я знаю, (что?) что он придёт.

2. <b>Определительные (отвечают на вопросы какой? который?)</b>
• Союзные слова: КОТОРЫЙ, КАКОЙ, ЧЕЙ
Пример: Книга, (какая?) которую я читаю, интересная.

3. <b>Обстоятельственные:</b>

🕐 Времени (когда? как долго?)
• Союзы: КОГДА, ПОКА, В ТО ВРЕМЯ КАК
Пример: Когда наступит весна, прилетят птицы.

📍 Места (где? куда? откуда?)
• Союзные слова: ГДЕ, КУДА, ОТКУДА
Пример: Я пойду туда, где растут цветы.

❓ Причины (почему? отчего?)
• Союзы: ПОТОМУ ЧТО, ТАК КАК, ОТТОГО ЧТО
Пример: Я не пошёл гулять, потому что шёл дождь.

🎯 Цели (зачем? для чего?)
• Союзы: ЧТОБЫ, ДЛЯ ТОГО ЧТОБЫ
Пример: Я учусь, чтобы получить знания.

❗️ Условия (при каком условии?)
• Союзы: ЕСЛИ, РАНЬШЕ
Пример: Если пойдёт дождь, мы останемся дома.

💭 Уступки (несмотря на что?)
• Союзы: ХОТЯ, НЕСМОТРЯ НА ТО ЧТО
Пример: Хотя было холодно, мы пошли гулять.""",

    'structure': """<b>Виды подчинения в СПП</b>

В сложноподчинённом предложении может быть несколько придаточных частей. Разберём, как они могут быть связаны:

1. <b>Последовательное подчинение</b>
• Придаточные зависят друг от друга как звенья цепи
• Первое придаточное зависит от главного
• Второе зависит от первого придаточного
• Третье от второго и так далее

Пример:
Я знаю (главное),
    что он сказал (1-е придаточное),
        когда вернётся домой (2-е придаточное).

2. <b>Параллельное подчинение</b>
• Все придаточные относятся к одному слову в главном
• Отвечают на разные вопросы
• Не зависят друг от друга

Пример:
Я вернусь домой (главное),
    когда закончу работу (1-е придаточное),
    хотя уже будет поздно (2-е придаточное).

3. <b>Однородное подчинение</b>
• Придаточные отвечают на один вопрос
• Относятся к одному слову в главном
• Связаны между собой сочинительной связью (и, или)

Пример:
Учитель сказал (главное),
    что контрольная будет завтра (1-е придаточное)
    и что надо повторить правила (2-е придаточное).""",

    'examples': """<b>Разбираем СПП на примерах</b>

1. <b>Изъяснительное придаточное:</b>
Я знаю, что завтра будет солнечно.
Разбор:
• Главная часть: Я знаю
• Придаточная часть: что завтра будет солнечно
• Вопрос: что я знаю?
• Союз: ЧТО

2. <b>Определительное придаточное:</b>
Книга, которую я читаю, очень интересная.
Разбор:
• Главная часть: Книга очень интересная
• Придаточная часть: которую я читаю
• Вопрос: какая книга?
• Союзное слово: КОТОРУЮ

3. <b>Придаточное времени:</b>
Когда наступит весна, прилетят птицы.
Разбор:
• Главная часть: прилетят птицы
• Придаточная часть: когда наступит весна
• Вопрос: когда прилетят?
• Союз: КОГДА

4. <b>Придаточное причины:</b>
Я взял зонт, потому что обещали дождь.
Разбор:
• Главная часть: Я взял зонт
• Придаточная часть: потому что обещали дождь
• Вопрос: почему взял?
• Союз: ПОТОМУ ЧТО

5. <b>Сложное СПП с разными придаточными:</b>
Я знаю, что, когда придёт весна, всё изменится.
Разбор:
• Главная часть: Я знаю
• 1-е придаточное: что всё изменится
• 2-е придаточное: когда придёт весна
• Тип подчинения: последовательное

<b>Важные моменты:</b>
• Всегда определяйте главную часть
• Задавайте вопрос к придаточной части
• Обращайте внимание на союзы и союзные слова
• Помните о знаках препинания между частями""",

    'punctuation': """<b>Знаки препинания в СПП</b>

1. <b>Запятая ставится:</b>
• Между главной и придаточной частями
• Перед союзами ЧТО, ЧТОБЫ, ЕСЛИ, КОГДА и др.
• Перед союзными словами КОТОРЫЙ, ГДЕ, КУДА и др.

Примеры:
🔹 Я знаю, что он придёт.
🔹 Когда начался дождь, мы пошли домой.

2. <b>Две запятые ставятся:</b>
• Если придаточное стоит внутри главного
• При причастных оборотах с КОТОРЫЙ

Примеры:
🔹 Книга, которую я читаю, очень интересная.
🔹 Дом, где я живу, находится в центре.

3. <b>НЕ ставится запятая:</b>
• Перед второй частью составного союза:
- то
- так
- но

Примеры:
🔹 Если пойдёт дождь, то мы останемся дома.
🔹 Хотя было холодно, но мы пошли гулять.

4. <b>Особые случаи:</b>

При однородных придаточных:
• Запятая между придаточными с повторяющимися союзами
🔹 Я знал, что он умный, что он добрый, что он честный.

• Без запятой, если союз НЕ повторяется
🔹 Я знал, что он умный и что он добрый.

При стыке союзов:
• Запятая между союзами ставится, если дальше нет союза ТО
🔹 Я знал, что, когда он придёт, мы поговорим.

• Запятая НЕ ставится, если дальше есть союз ТО
🔹 Я знал, что если он придёт, то мы поговорим.

5. <b>Подсказки для проверки:</b>

• Задайте вопрос от главной части к придаточной
• Найдите союз или союзное слово
• Определите границы придаточного предложения
• Проверьте, не является ли союз составным

<b>Примеры с разбором:</b>

1. Я точно знаю, что завтра будет хорошая погода.
• Запятая перед союзом ЧТО
• Одно придаточное

2. Когда наступит весна, природа оживёт.
• Запятая после придаточного в начале
• Союз КОГДА

3. Мы пойдём гулять, если закончится дождь.
• Запятая перед союзом ЕСЛИ
• Придаточное в конце

4. Я уверен, что, хотя задача сложная, мы справимся.
• Запятые выделяют придаточное ХОТЯ
• Стык союзов ЧТО и ХОТЯ"""
}

# Клавиатура для БСП
def get_bsp_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Что такое БСП", callback_data="bsp_main")],
        [InlineKeyboardButton(text="❗️ Знаки препинания", callback_data="bsp_punctuation")],
        [InlineKeyboardButton(text="🔄 Смысловые отношения", callback_data="bsp_relations")],
        [InlineKeyboardButton(text="📚 Примеры с разбором", callback_data="bsp_examples")],
        [InlineKeyboardButton(text="◀️ Назад к разделам", callback_data="show_theory")]
    ])
bsp_theory = {
    'main': """<b>Что такое бессоюзное сложное предложение (БСП)?</b>

Простыми словами: это сложное предложение, части которого связаны без помощи союзов, только по смыслу и интонацией.

<b>Как узнать БСП?</b>
1. Смотрим на части предложения:
• Несколько простых предложений
• Между ними нет союзов
• Части разделены запятой, точкой с запятой, двоеточием или тире

2. Проверяем интонацию:
• Перечисление
• Пояснение
• Противопоставление
• Условие-следствие

<b>Примеры:</b>
🔹 Солнце светит, птицы поют.
• Две части без союзов
• Перечисление действий
• Запятая между частями

🔹 Я посмотрел в окно: шёл снег.
• Две части без союзов
• Вторая часть поясняет первую
• Двоеточие между частями

<b>Важно помнить:</b>
• Части БСП всегда разделяются знаками препинания
• Смысл можно понять по интонации
• Между частями можно вставить союзы, но они не нужны""",

    'punctuation': """<b>Знаки препинания в БСП</b>

1. <b>ЗАПЯТАЯ (,) ставится, если:</b>
• Перечисляются события
• Действия происходят одновременно
• Действия следуют одно за другим

Примеры:
🔹 Солнце светит, птицы поют, листья шелестят.
(перечисление)
🔹 Ветер воет, дождь стучит по крыше.
(одновременные действия)

2. <b>ТОЧКА С ЗАПЯТОЙ (;) ставится, если:</b>
• Части сильно распространены
• Внутри частей есть запятые
• Нужно показать большую паузу

Пример:
🔹 Солнце медленно опускалось за горизонт, окрашивая небо в розовые тона; птицы постепенно затихали, готовясь к ночному отдыху.

3. <b>ДВОЕТОЧИЕ (:) ставится, если вторая часть:</b>
• Поясняет первую (можно вставить А ИМЕННО)
• Указывает причину (можно вставить ПОТОМУ ЧТО)
• Дополняет первую (можно вставить ЧТО)

Примеры:
🔹 Я не пошёл гулять: на улице шёл дождь.
(причина)
🔹 Я понял одно: нужно больше учиться.
(пояснение)

4. <b>ТИРЕ (-) ставится, если:</b>
• Содержится противопоставление
• Показывается результат, следствие
• Указывается время или условие
• Действия быстро сменяют друг друга

Примеры:
🔹 Сделал дело - гуляй смело.
(условие-следствие)
🔹 Сверкнула молния - грянул гром.
(быстрая смена событий)""",

    'relations': """<b>Смысловые отношения между частями БСП</b>

1. <b>Перечисление</b>
• Действия происходят одновременно
• События следуют друг за другом
• Ставится запятая

Пример:
🔹 Светит солнце, поют птицы, шумит лес.
• Всё происходит одновременно
• Можно добавить союз И

2. <b>Пояснение</b>
• Вторая часть объясняет первую
• Раскрывает её смысл
• Ставится двоеточие

Пример:
🔹 Я понял главное: нужно много работать.
• Вторая часть поясняет, что именно понял
• Можно добавить А ИМЕННО

3. <b>Причина и следствие</b>
• Одна часть объясняет причину
• Другая показывает результат
• Ставится двоеточие или тире

Примеры:
🔹 Я не выспался: всю ночь готовился к экзамену.
(причина - двоеточие)
🔹 Пришла весна - прилетели птицы.
(следствие - тире)

4. <b>Условие</b>
• Первая часть - условие
• Вторая часть - результат
• Ставится тире

Пример:
🔹 Много будешь читать - много будешь знать.
• Условие: если будешь читать
• Результат: будешь знать

5. <b>Время</b>
• Показывает последовательность
• Быструю смену событий
• Ставится тире

Пример:
🔹 Солнце взошло - начался новый день.
• Последовательность событий
• Можно добавить КОГДА""",

    'examples': """<b>Разбираем БСП на примерах</b>

1. <b>БСП с запятой:</b>
Солнце светит, птицы поют, листья шелестят.
Разбор:
• Три простые части
• Перечисление событий
• Всё происходит одновременно
• Можно добавить И: Солнце светит, и птицы поют, и листья шелестят

2. <b>БСП с двоеточием (причина):</b>
Я не пошёл гулять: на улице шёл дождь.
Разбор:
• Две части
• Вторая часть объясняет причину
• Можно добавить ПОТОМУ ЧТО: Я не пошёл гулять, потому что на улице шёл дождь

3. <b>БСП с двоеточием (пояснение):</b>
Я понял одно: нужно больше заниматься.
Разбор:
• Две части
• Вторая часть поясняет первую
• Можно добавить А ИМЕННО: Я понял одно, а именно нужно больше заниматься

4. <b>БСП с тире (следствие):</b>
Прозвенел звонок - начался урок.
Разбор:
• Две части
• Вторая часть показывает результат
• Можно добавить И ПОЭТОМУ: Прозвенел звонок, и поэтому начался урок

5. <b>БСП с тире (условие):</b>
Любишь кататься - люби и саночки возить.
Разбор:
• Две части
• Первая часть - условие
• Можно добавить ЕСЛИ: Если любишь кататься, люби и саночки возить

<b>Важные моменты:</b>
• Всегда определяйте смысловые отношения между частями
• Проверяйте, какой союз можно вставить
• Выбирайте знак препинания в зависимости от смысла
• Обращайте внимание на интонацию при чтении"""}


@dp.callback_query(lambda c: c.data == "show_ssp")
async def show_ssp(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Что такое ССП", callback_data="ssp_main")],
        [InlineKeyboardButton(text="🔄 Союзы в ССП", callback_data="ssp_unions")],
        [InlineKeyboardButton(text="❗️ Знаки препинания", callback_data="ssp_punctuation")],
        [InlineKeyboardButton(text="📚 Примеры с разбором", callback_data="ssp_examples")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_theory")]
    ])
    await callback.message.edit_text("Сложносочинённое предложение (ССП)", reply_markup=kb)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "show_spp")
async def show_spp(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Что такое СПП", callback_data="spp_main")],
        [InlineKeyboardButton(text="🔄 Виды придаточных", callback_data="spp_types")],
        [InlineKeyboardButton(text="❗️ Знаки препинания", callback_data="spp_punctuation")],  # Новая кнопка
        [InlineKeyboardButton(text="📚 Виды подчинения", callback_data="spp_structure")],
        [InlineKeyboardButton(text="📋 Примеры с разбором", callback_data="spp_examples")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_theory")]
    ])
    await callback.message.edit_text("Сложноподчинённое предложение (СПП)", reply_markup=kb)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "show_bsp")
async def show_bsp(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Что такое БСП", callback_data="bsp_main")],
        [InlineKeyboardButton(text="❗️ Знаки препинания", callback_data="bsp_punctuation")],
        [InlineKeyboardButton(text="🔄 Смысловые отношения", callback_data="bsp_relations")],
        [InlineKeyboardButton(text="📚 Примеры с разбором", callback_data="bsp_examples")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_theory")]
    ])
    await callback.message.edit_text("Бессоюзное сложное предложение (БСП)", reply_markup=kb)
    await callback.answer()

@dp.callback_query(lambda c: c.data == "back_to_theory")
async def back_to_theory(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="ССП", callback_data="show_ssp"),
            InlineKeyboardButton(text="СПП", callback_data="show_spp"),
            InlineKeyboardButton(text="БСП", callback_data="show_bsp")
        ]
    ])
    await callback.message.edit_text("📚 Выберите раздел теории:", reply_markup=kb)
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith(("ssp_", "spp_", "bsp_")))
async def process_theory_section(callback: CallbackQuery):
    section_type, section = callback.data.split('_')
    theory_dict = None
    back_command = None

    if section_type == "ssp":
        theory_dict = ssp_theory
        back_command = "show_ssp"
    elif section_type == "spp":
        theory_dict = spp_theory
        back_command = "show_spp"
    elif section_type == "bsp":
        theory_dict = bsp_theory
        back_command = "show_bsp"

    if theory_dict and section in theory_dict:
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="◀️ Назад", callback_data=back_command)]
        ])
        await callback.message.edit_text(
            theory_dict[section],
            reply_markup=kb,
            parse_mode=ParseMode.HTML
        )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("ssp_"))
async def process_ssp_callback(callback: CallbackQuery):
    section = callback.data.split("_")[1]

    if section in ssp_theory:
        await callback.message.edit_text(
            ssp_theory[section],
            reply_markup=get_ssp_keyboard(),
            parse_mode=ParseMode.HTML
        )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "show_ssp")
async def show_ssp(callback: CallbackQuery):
    await callback.message.edit_text(
        ssp_theory['main'],
        reply_markup=get_ssp_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("spp_"))
async def process_spp_callback(callback: CallbackQuery):
    section = callback.data.split("_")[1]

    if section in spp_theory:
        await callback.message.edit_text(
            spp_theory[section],
            reply_markup=get_spp_keyboard(),
            parse_mode=ParseMode.HTML
        )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "show_spp")
async def show_spp(callback: CallbackQuery):
    await callback.message.edit_text(
        spp_theory['main'],
        reply_markup=get_spp_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()

@dp.callback_query(lambda c: c.data.startswith("bsp_"))
async def process_bsp_callback(callback: CallbackQuery):
    section = callback.data.split("_")[1]

    if section in bsp_theory:
        await callback.message.edit_text(
            bsp_theory[section],
            reply_markup=get_bsp_keyboard(),
            parse_mode=ParseMode.HTML
        )
    await callback.answer()

@dp.callback_query(lambda c: c.data == "show_bsp")
async def show_bsp(callback: CallbackQuery):
    await callback.message.edit_text(
        bsp_theory['main'],
        reply_markup=get_bsp_keyboard(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


async def reset_daily_limits():
    while True:
        try:
            now = datetime.now()
            for user_id in list(user_last_tasks.keys()):
                last_task_time = datetime.strptime(user_last_tasks[user_id], "%Y-%m-%d %H:%M:%S")
                if now - last_task_time >= timedelta(hours=6):
                    del user_last_tasks[user_id]
            await asyncio.sleep(300)  # Проверяем каждые 5 минут
        except Exception as e:
            logging.error(f"Error in reset_daily_limits: {e}")
            await asyncio.sleep(300)


async def send_task(user_id: int, task: dict):
    try:
        if task['type'] == 'type6':
            # Сначала отправляем схему с начальным текстом
            await bot.send_photo(
                user_id,
                FSInputFile(task['image']),
                caption=f"Дополните предложение по схеме:\n\n{task['start_text']}"
            )

            # Формируем текст с вариантами продолжения и отправляем отдельным сообщением
            variants_text = "Варианты продолжения:\n\n"
            variants_text += "\n\n".join(task['sentences'])

            # Отправляем варианты и клавиатуру
            await bot.send_message(
                user_id,
                variants_text,
                reply_markup=task['keyboard'],
                parse_mode=ParseMode.HTML
            )

        elif task['type'] == 'type5':
            # Сначала отправляем фото со схемой
            await bot.send_photo(
                user_id,
                FSInputFile(task['image']),
                caption="Выберите предложение, которое соответствует схеме на фото:"
            )

            # Формируем текст с предложениями и отправляем отдельным сообщением
            sentences_text = "\n\n".join(task['sentences'])

            # Отправляем текст с вариантами и клавиатурой
            await bot.send_message(
                user_id,
                sentences_text,
                reply_markup=task['keyboard'],
                parse_mode=ParseMode.HTML
            )

        elif task['type'] in ['type1', 'type2', 'type3']:
            # Для заданий с выбором ответа
            keyboard = task.get('keyboard', None)
            await bot.send_photo(
                user_id,
                FSInputFile(task['image']),
                reply_markup=keyboard
            )

        elif task['type'] == 'type4':
            # Для заданий с вводом ответа
            await bot.send_photo(
                user_id,
                FSInputFile(task['image'])
            )
            await bot.send_message(
                user_id,
                task['instruction'],
                parse_mode=ParseMode.HTML
            )

        # Добавляем запись в лог об успешной отправке
        logging.info(f"Task {task['id']} sent to user {user_id}")

    except FileNotFoundError as e:
        error_msg = f"Файл изображения не найден для задания {task['id']}: {e}"
        logging.error(error_msg)
        await bot.send_message(
            user_id,
            "Извините, произошла ошибка при загрузке изображения. Попробуйте другое задание."
        )

    except Exception as e:
        error_msg = f"Ошибка при отправке задания {task['id']}: {e}"
        logging.error(error_msg)
        await bot.send_message(
            user_id,
            "Произошла ошибка при отправке задания. Пожалуйста, попробуйте позже или используйте /start для перезапуска бота."
        )

        # Добавляем более подробное логирование ошибки
        logging.error(f"Полная информация об ошибке для задания {task['id']}:")
        logging.error(f"Тип задания: {task['type']}")
        logging.error(f"Пользователь: {user_id}")
        logging.error(f"Детали ошибки: {str(e)}")


def get_available_tasks(user_id: int) -> list:
    if user_id not in user_completed_tasks:
        user_completed_tasks[user_id] = set()

    available_task_ids = set(task['id'] for task in BD) - user_completed_tasks[user_id]

    if not available_task_ids:
        user_completed_tasks[user_id].clear()
        available_task_ids = set(task['id'] for task in BD)

    available_tasks = [task for task in BD if task['id'] in available_task_ids]
    return available_tasks


# Стикеры по категориям
STICKERS = {
    'perfect': [
        'CAACAgIAAxkBAAEPaR1oNLX34uD_61cFwt9KoY85I3rY8AACKHkAAh_soUmA86g1AXLZSjYE',  # радость
        'CAACAgIAAxkBAAEPaR9oNLX5ivjWA6GZnuhV2zmM-VQy-QACM3MAAvb0oUmOGcvqKySJrjYE',  # победа
        'CAACAgIAAxkBAAEPaSFoNLX73ZIhxNNfHZLzxkP7Yn7a-gACUHMAAnlXqUkmY71FJ17GbzYE'  # супер
    ],
    'good': [
        'CAACAgIAAxkBAAEPaSdoNLYlHQlsbE0Radj8KPNMDsGdggACNXUAAnslMEjJ61Q1lr2WFjYE',  # молодец
        'CAACAgIAAxkBAAEPaSVoNLYb6xxfbtYuuICg3uMbQXzBSgACEm4AAlAIqUmnvth6C_VjiTYE',  # хорошо
        'CAACAgIAAxkBAAEPaSNoNLYVoXU9O6q-s_KKe__1-vQohAACB5UAAhlMqEnv7C7jyXp3tjYE'  # неплохо
    ],
    'wrong': [
        'CAACAgIAAxkBAAEPaS1oNLZZpb0KXXyOmreTye-MhRj2jAAC9nYAApVmqElWpO-xZ0foHjYE',  # ошибка
        'CAACAgIAAxkBAAEPaSloNLZBPmWZw284uRP0BMnv020PQgACUmYAAvKxOUi3XvTrn847TzYE',  # подумай
        'CAACAgIAAxkBAAEPaStoNLZPMIuGYZS5z4f_lGFFNJaN6gACWHkAAtHnqEmPh79aeC-3TDYE'  # неверно
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



def save_user_data():
    try:
        data = {
            'users': {
                str(user_id): {
                    'username': user_info['username'],
                    'reg_date': user_info['reg_date'],
                    'tasks_completed': user_info['tasks_completed'],
                    'last_active': user_info['last_active'],
                    'total_answers': user_info.get('total_answers', 0),
                    'correct_answers': user_info.get('correct_answers', 0),
                    'best_streak': user_info.get('best_streak', 0),
                    'accuracy': user_info.get('accuracy', 0.0)
                }
                for user_id, user_info in users.items()
            },
            'user_streaks': {str(k): v for k, v in user_streaks.items()},
            'user_completed_tasks': {
                str(user_id): list(tasks)
                for user_id, tasks in user_completed_tasks.items()
            },
            'user_last_tasks': {
                str(user_id): time
                for user_id, time in user_last_tasks.items()
            },
            'last_save': datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        }

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logging.info(f"User data saved successfully: {data}")
    except Exception as e:
        logging.error(f"Error saving user data: {e}")


def load_user_data():
    try:
        if not os.path.exists(DATA_FILE):
            logging.info("No saved data file found")
            return

        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # Загружаем данные пользователей
            loaded_users = data.get('users', {})
            for user_id_str, user_info in loaded_users.items():
                user_id = int(user_id_str)
                users[user_id] = {
                    'username': user_info['username'],
                    'reg_date': user_info['reg_date'],
                    'tasks_completed': user_info['tasks_completed'],
                    'last_active': user_info['last_active'],
                    'total_answers': user_info.get('total_answers', 0),
                    'correct_answers': user_info.get('correct_answers', 0),
                    'best_streak': user_info.get('best_streak', 0),
                    'accuracy': user_info.get('accuracy', 0.0)
                }

            # Загружаем серии
            loaded_streaks = data.get('user_streaks', {})
            for user_id_str, streak in loaded_streaks.items():
                user_streaks[int(user_id_str)] = streak

            # Загружаем выполненные задания
            loaded_completed = data.get('user_completed_tasks', {})
            for user_id_str, tasks in loaded_completed.items():
                user_completed_tasks[int(user_id_str)] = set(tasks)

            # Загружаем время последних заданий
            loaded_last_tasks = data.get('user_last_tasks', {})
            for user_id_str, time in loaded_last_tasks.items():
                user_last_tasks[int(user_id_str)] = time

        logging.info("User data loaded successfully")
        logging.info(f"Loaded users data: {users}")
    except Exception as e:
        logging.error(f"Error loading user data: {e}")


async def auto_save():
    while True:
        try:
            save_user_data()
            await asyncio.sleep(3600)  # 1 час
        except Exception as e:
            logging.error(f"Error in auto_save: {e}")
            await asyncio.sleep(300)  # При ошибке подождем 5 минут


@dp.callback_query(lambda c: c.data.startswith("ans_"))
async def check_answer(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        if user_id not in user_tasks:
            await callback.answer("Нет активного задания")
            return

        # Проверяем и инициализируем поля статистики, если их нет
        if user_id not in users:
            users[user_id] = {
                "username": callback.from_user.username or "Пользователь",
                "reg_date": datetime.now().strftime("%d.%m.%Y"),
                "tasks_completed": 0,
                "last_active": datetime.now().strftime("%d.%m.%Y"),
                "total_answers": 0,
                "correct_answers": 0,
                "best_streak": 0
            }
        elif 'total_answers' not in users[user_id]:
            users[user_id].update({
                "total_answers": 0,
                "correct_answers": 0,
                "best_streak": 0
            })

        user = user_tasks[user_id]
        task = user['tasks'][user['current']]
        answer = callback.data.split("_")[1]

        # Увеличиваем счетчик всех ответов
        users[user_id]['total_answers'] += 1

        is_correct = answer == task['correct']

        if is_correct:
            users[user_id]['correct_answers'] += 1
            user['correct'] += 1
            sticker_category = 'perfect' if user['correct'] > 2 else 'good'
            await callback.message.answer_sticker(random.choice(STICKERS[sticker_category]))
            await callback.message.answer(random.choice(MESSAGES[sticker_category]))
        else:
            await callback.message.answer_sticker(random.choice(STICKERS['wrong']))
            await callback.message.answer(
                f"{random.choice(MESSAGES['wrong'])}\n\n"
                f"📝 Пояснение:\n{task['explanation']}\n\n"
                f"✨ Правильный ответ: {task['correct']}"
            )

        await callback.message.edit_reply_markup(reply_markup=None)

        user['current'] += 1
        if user['current'] < len(user['tasks']):
            await asyncio.sleep(2)
            await send_task(user_id, user['tasks'][user['current']])
        else:
            await show_results(user_id, callback.message)

        await callback.answer()
        save_rating_data()

    except Exception as e:
        logging.error(f"Error in check_answer: {e}")
        user_id = callback.from_user.id
        if user_id in user_tasks:
            del user_tasks[user_id]
        await callback.message.answer(
            "Произошла ошибка. Используйте /start для новой попытки."
        )


async def show_results(user_id: int, message: types.Message):
    try:
        user = user_tasks[user_id]
        correct = user['correct']
        total = len(user['tasks'])

        # Обновляем статистику
        if user_id in users:
            users[user_id]["tasks_completed"] += correct
            users[user_id]["last_active"] = datetime.now().strftime("%d.%m.%Y")

        # Проверяем результат
        if correct == total:  # Все ответы правильные
            # Проверяем, можно ли обновить стрик сегодня
            current_time = datetime.now()
            last_time = last_streak_time.get(user_id)

            if last_time is None or (current_time - last_time).days >= 1:
                # Прошло более 24 часов с последнего стрика
                user_streaks[user_id] = user_streaks.get(user_id, 0) + 1
                last_streak_time[user_id] = current_time

                result = (
                    f"🎉 *Великолепный результат!*\n"
                    f"📊 Счет: {correct}/{total}\n"
                    f"🔥 Серия: {user_streaks[user_id]}\n"
                    f"Возвращайтесь завтра, чтобы продолжить серию!"
                )
            else:
                # Стрик уже был обновлен сегодня
                result = (
                    f"🎉 *Великолепный результат!*\n"
                    f"📊 Счет: {correct}/{total}\n"
                    f"🔥 Текущая серия: {user_streaks[user_id]}\n"
                    f"Серия уже обновлена сегодня. Приходите завтра!"
                )
            category = 'perfect'

        elif correct >= total * 0.7:  # Хороший результат, но не идеальный
            # Сбрасываем стрик при любой ошибке
            if user_id in user_streaks:
                old_streak = user_streaks[user_id]
                del user_streaks[user_id]
                if user_id in last_streak_time:
                    del last_streak_time[user_id]
                result = (
                    f"👍 *Хороший результат!*\n"
                    f"📊 Счет: {correct}/{total}\n"
                    f"❌ Серия прервана! Было: {old_streak}\n"
                    f"Для новой серии нужны все правильные ответы!"
                )
            else:
                result = (
                    f"👍 *Хороший результат!*\n"
                    f"📊 Счет: {correct}/{total}"
                )
            category = 'good'

        else:  # Плохой результат
            # Сбрасываем стрик
            if user_id in user_streaks:
                old_streak = user_streaks[user_id]
                del user_streaks[user_id]
                if user_id in last_streak_time:
                    del last_streak_time[user_id]
                result = (
                    f"📚 *Есть куда расти!*\n"
                    f"📊 Счет: {correct}/{total}\n"
                    f"❌ Серия прервана! Было: {old_streak}\n"
                    f"Для новой серии нужны все правильные ответы!"
                )
            else:
                result = (
                    f"📚 *Есть куда расти!*\n"
                    f"📊 Счет: {correct}/{total}"
                )
            category = 'wrong'

        await message.answer_sticker(random.choice(STICKERS[category]))
        await message.answer(result, parse_mode=ParseMode.MARKDOWN)

        # Сохраняем обновленные данные
        save_rating_data()

    except Exception as e:
        logging.error(f"Error in show_results: {e}")
        await message.answer(
            "Произошла ошибка при показе результатов. Используйте /start для начала новой сессии."
        )


@dp.callback_query(lambda c: c.data in ["next_training", "end_training"])
async def process_training_action(callback: CallbackQuery):
    user_id = callback.from_user.id

    if callback.data == "next_training":
        sentence = random.choice(training_sentences)
        user_training_data[user_id] = sentence

        await callback.message.answer(
            "Перепишите предложение, расставляя знаки препинания:\n\n"
            f"{sentence['sentence']}"
        )
    else:  # end_training
        if user_id in user_training_state:
            del user_training_state[user_id]
        if user_id in user_training_data:
            del user_training_data[user_id]

        await callback.message.answer(
            "Тренировка завершена! Возвращаемся в главное меню.",
            reply_markup=main_kb
        )

    await callback.answer()


# Функции для сохранения и загрузки рейтинга
def save_rating_data():
    try:
        rating_data = {
            'users': {
                str(user_id): {
                    'username': user_info['username'],
                    'reg_date': user_info['reg_date'],
                    'tasks_completed': user_info['tasks_completed'],
                    'last_active': user_info['last_active'],
                    'total_answers': user_info.get('total_answers', 0),
                    'correct_answers': user_info.get('correct_answers', 0),
                    'best_streak': user_info.get('best_streak', 0),
                    'accuracy': user_info.get('accuracy', 0.0)
                }
                for user_id, user_info in users.items()
            },
            'user_streaks': {
                str(user_id): int(streak)
                for user_id, streak in user_streaks.items()
            },
            'subscribed_users': list(subscribed_users),
            'user_next_notification': {
                str(user_id): time.strftime("%Y-%m-%d %H:%M:%S")
                for user_id, time in user_next_notification.items()
            },
            'last_save': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(RATING_FILE, 'w', encoding='utf-8') as f:
            json.dump(rating_data, f, ensure_ascii=False, indent=2)
        logging.info("Rating data saved successfully")

    except Exception as e:
        logging.error(f"Error saving rating data: {e}")


def load_rating_data():
    try:
        if not os.path.exists(RATING_FILE):
            logging.info("No rating data file found")
            return

        with open(RATING_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Загружаем данные пользователей
        for user_id_str, user_info in data.get('users', {}).items():
            user_id = int(user_id_str)
            if user_id not in users:
                users[user_id] = {}
            users[user_id] = {
                'username': user_info['username'],
                'reg_date': user_info['reg_date'],
                'tasks_completed': user_info['tasks_completed'],
                'last_active': user_info['last_active'],
                'total_answers': user_info.get('total_answers', 0),
                'correct_answers': user_info.get('correct_answers', 0),
                'best_streak': user_info.get('best_streak', 0),
                'accuracy': user_info.get('accuracy', 0.0)
            }

        # Загружаем серии
        for user_id_str, streak in data.get('user_streaks', {}).items():
            user_streaks[int(user_id_str)] = int(streak)

        # Загружаем данные уведомлений
        subscribed_users.update(int(user_id) for user_id in data.get('subscribed_users', []))

        for user_id_str, time_str in data.get('user_next_notification', {}).items():
            user_next_notification[int(user_id_str)] = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")

        logging.info("Rating data loaded successfully")

    except Exception as e:
        logging.error(f"Error loading rating data: {e}")


training_sentences = [
    # ССП (Сложносочиненные предложения)
    {
        'sentence': "Солнце еще не взошло но птицы уже начали свою утреннюю песню",
        'correct': "Солнце еще не взошло, но птицы уже начали свою утреннюю песню.",
        'explanation': "Запятая ставится перед противительным союзом 'но', соединяющим части сложносочиненного предложения."
    },
    {
        'sentence': "Ночь грозою бушевала и молнии озаряли гряду отдалённых холмов",
        'correct': "Ночь грозою бушевала, и молнии озаряли гряду отдалённых холмов.",
        'explanation': "Запятая ставится перед соединительным союзом 'и', соединяющим две грамматические основы."
    },
    {
        'sentence': "Берёзы за одну ночь пожелтели до самых макушек и листья сыпались с них частым и печальным дождём",
        'correct': "Берёзы за одну ночь пожелтели до самых макушек, и листья сыпались с них частым и печальным дождём.",
        'explanation': "Запятая ставится перед союзом 'и', соединяющим две части сложносочиненного предложения."
    },
    {
        'sentence': "Отгремел грозами июль и лето вдруг сразу перемахнуло на осень",
        'correct': "Отгремел грозами июль, и лето вдруг сразу перемахнуло на осень.",
        'explanation': "Запятая ставится перед союзом 'и', так как он соединяет две части сложносочиненного предложения с разными подлежащими и сказуемыми."
    },
    {
        'sentence': "Гроза отходит на северо-восток и оттуда доносится неумолчный рокот разгневанных туч",
        'correct': "Гроза отходит на северо-восток, и оттуда доносится неумолчный рокот разгневанных туч.",
        'explanation': "Запятая ставится перед союзом 'и', соединяющим две части сложносочиненного предложения с разными грамматическими основами."
    },

    # СПП (Сложноподчиненные предложения)
    {
        'sentence': "Ночь была такая плотная что вплотную столкнувшись лицами нельзя было видеть друг друга",
        'correct': "Ночь была такая плотная, что вплотную столкнувшись лицами, нельзя было видеть друг друга.",
        'explanation': "Запятая ставится перед союзом 'что' в сложноподчиненном предложении, вторая запятая выделяет деепричастный оборот."
    },
    {
        'sentence': "При мысли великой что я человек всегда возвышаюсь душою",
        'correct': "При мысли великой, что я человек, всегда возвышаюсь душою.",
        'explanation': "Запятыми выделяется придаточное предложение, стоящее внутри главного."
    },
    {
        'sentence': "Несмотря на то что было холодно снег таял совсем незаметно",
        'correct': "Несмотря на то что было холодно, снег таял совсем незаметно.",
        'explanation': "Запятая ставится после придаточного предложения с составным союзом 'несмотря на то что'."
    },
    {
        'sentence': "Животные наверняка видели как мы ломали ветки и вероятно слышали наши голоса",
        'correct': "Животные наверняка видели, как мы ломали ветки, и, вероятно, слышали наши голоса.",
        'explanation': "Запятая ставится перед союзом 'как', вводное слово 'вероятно' выделяется запятыми."
    },
    {
        'sentence': "Когда начался дождь мы поспешили домой хотя до места оставалось совсем немного",
        'correct': "Когда начался дождь, мы поспешили домой, хотя до места оставалось совсем немного.",
        'explanation': "Запятые ставятся после придаточного времени и перед придаточным уступки."
    },

    # БСП (Бессоюзные сложные предложения)
    {
        'sentence': "Надо было всё обдумать вспомнить не забыл ли чего",
        'correct': "Надо было всё обдумать, вспомнить, не забыл ли чего.",
        'explanation': "Запятые ставятся между частями бессоюзного сложного предложения при перечислении."
    },
    {
        'sentence': "Лес горы слились всё окуталось густым туманом",
        'correct': "Лес, горы слились, всё окуталось густым туманом.",
        'explanation': "Запятая ставится между однородными подлежащими и частями бессоюзного сложного предложения."
    },
    {
        'sentence': "Кругом было тихо и безлюдно не было слышно даже всплесков прибоя",
        'correct': "Кругом было тихо и безлюдно, не было слышно даже всплесков прибоя.",
        'explanation': "Запятая разделяет части бессоюзного сложного предложения."
    },
    {
        'sentence': "День заканчивался тени гор спускались в долину",
        'correct': "День заканчивался, тени гор спускались в долину.",
        'explanation': "Запятая разделяет части бессоюзного сложного предложения, между которыми перечисляются происходящие события."
    },
    {
        'sentence': "Был вечер на небе блестели яркие звезды",
        'correct': "Был вечер, на небе блестели яркие звезды.",
        'explanation': "Запятая разделяет части бессоюзного сложного предложения, где вторая часть дополняет первую."
    },
    # Добавляем новые предложения в training_sentences:

    # Предложения с разными видами связи
    {
        'sentence': "В ожидании ужина мы сидели у костра наблюдая как на реке угасает последний отсвет мутного заката и прислушиваясь к порывистому дыханию переката у изголовья заводи",
        'correct': "В ожидании ужина мы сидели у костра, наблюдая, как на реке угасает последний отсвет мутного заката, и прислушиваясь к порывистому дыханию переката у изголовья заводи.",
        'explanation': "Запятыми выделяются деепричастные обороты, также запятая ставится перед союзом 'как' в придаточном предложении."
    },
    {
        'sentence': "Солнце медленно сползает с неба на край степи и когда оно почти касается земли становится багровым",
        'correct': "Солнце медленно сползает с неба на край степи, и когда оно почти касается земли, становится багровым.",
        'explanation': "Запятая ставится перед союзом 'и', а придаточное предложение с союзом 'когда' выделяется запятыми с двух сторон."
    },
    {
        'sentence': "Родители провожали детей на отдых и когда поезд тронулся долго махали им вслед",
        'correct': "Родители провожали детей на отдых, и когда поезд тронулся, долго махали им вслед.",
        'explanation': "Запятая ставится перед союзом 'и', придаточное предложение времени выделяется запятыми."
    },
    {
        'sentence': "Мы сидели на полу и недоуменно глядя друг на друга гадали куда запропастился ежик",
        'correct': "Мы сидели на полу и, недоуменно глядя друг на друга, гадали, куда запропастился ежик.",
        'explanation': "Запятыми выделяется деепричастный оборот, также запятая ставится перед союзным словом 'куда'."
    },
    {
        'sentence': "С веками всё меньше становится даровых благ на земле и чтобы не знать горя впереди надо разумно тратить всякую копейку без расписки взятую у природы",
        'correct': "С веками всё меньше становится даровых благ на земле, и чтобы не знать горя впереди, надо разумно тратить всякую копейку, без расписки взятую у природы.",
        'explanation': "Запятые ставятся перед союзом 'и', после придаточного цели и перед причастным оборотом."
    },

    # Предложения с деепричастными оборотами
    {
        'sentence': "Накинув на плечо одностволку он подвинулся ближе к костру и наблюдая как пламя пожирает головёшки погрузился в свои думы",
        'correct': "Накинув на плечо одностволку, он подвинулся ближе к костру и, наблюдая, как пламя пожирает головёшки, погрузился в свои думы.",
        'explanation': "Запятыми выделяются деепричастные обороты, также запятая ставится перед союзом 'как'."
    },
    {
        'sentence': "Я пошёл быстро почти побежал и когда очутился на окраине тихой деревушки перевёл дух и утёр испарину со лба",
        'correct': "Я пошёл быстро, почти побежал, и когда очутился на окраине тихой деревушки, перевёл дух и утёр испарину со лба.",
        'explanation': "Запятые ставятся между однородными сказуемыми, перед союзом 'и' и выделяют придаточное предложение времени."
    },
    {
        'sentence': "Я валялся на койке то подрёмывая то слушая как близко и гулко барабанит дождь по крыше",
        'correct': "Я валялся на койке, то подрёмывая, то слушая, как близко и гулко барабанит дождь по крыше.",
        'explanation': "Запятыми выделяются деепричастные обороты с повторяющимися союзами 'то...то', также запятая ставится перед союзом 'как'."
    },
    {
        'sentence': "Вечером как только темнота скрыла картину моря и толчки волн стали ощущаться сильнее и резче пассажиры разбрелись по каютам",
        'correct': "Вечером, как только темнота скрыла картину моря и толчки волн стали ощущаться сильнее и резче, пассажиры разбрелись по каютам.",
        'explanation': "Запятыми выделяется придаточное предложение времени с составным союзом 'как только'."
    },
    {
        'sentence': "Утром ещё солнце не успело подняться мы уже покинули гостеприимный распадок",
        'correct': "Утром, ещё солнце не успело подняться, мы уже покинули гостеприимный распадок.",
        'explanation': "Запятыми выделяется придаточное предложение времени, стоящее между частями главного предложения."
    },
    # Предложения с причастными оборотами и определениями
    {
        'sentence': "Передо мной было большое круглое болото занесённое снегом из-под белой пелены которого торчали редкие кочки",
        'correct': "Передо мной было большое круглое болото, занесённое снегом, из-под белой пелены которого торчали редкие кочки.",
        'explanation': "Запятыми выделяется причастный оборот 'занесённое снегом', определительное придаточное с союзным словом 'которого' запятой не выделяется, так как оно стоит в середине предложения."
    },
    {
        'sentence': "Сказки отца от которых быть может пошла моя страсть к путешествиям распаляли воображение",
        'correct': "Сказки отца, от которых, быть может, пошла моя страсть к путешествиям, распаляли воображение.",
        'explanation': "Запятыми выделяется придаточное определительное с союзным словом 'которых' и вводное сочетание 'быть может'."
    },
    {
        'sentence': "Рожь гнулась и качалась на нивах лес синевший впереди побледнел расплылся и исчез",
        'correct': "Рожь гнулась и качалась на нивах, лес, синевший впереди, побледнел, расплылся и исчез.",
        'explanation': "Запятыми выделяется причастный оборот 'синевший впереди', запятые ставятся между частями бессоюзного предложения и однородными сказуемыми."
    },
    {
        'sentence': "Солнце ещё не поднялось из-за корявого березняка видневшегося поодаль но первые оранжевые лучи острыми иглами пробивались через листву",
        'correct': "Солнце ещё не поднялось из-за корявого березняка, видневшегося поодаль, но первые оранжевые лучи острыми иглами пробивались через листву.",
        'explanation': "Запятыми выделяется причастный оборот 'видневшегося поодаль', запятая ставится перед противительным союзом 'но'."
    },
    {
        'sentence': "Ветви орешника наклонились над деревом образуя зелёный навес сквозь ветви просвечивало небо в красках заката",
        'correct': "Ветви орешника наклонились над деревом, образуя зелёный навес, сквозь ветви просвечивало небо в красках заката.",
        'explanation': "Запятыми выделяется деепричастный оборот 'образуя зелёный навес', запятая ставится между частями бессоюзного предложения."
    },

    # Предложения с вводными словами и конструкциями
    {
        'sentence': "По мере того как он её слушал насмешливая улыбка оказалась на её губах",
        'correct': "По мере того как он её слушал, насмешливая улыбка оказалась на её губах.",
        'explanation': "Запятая ставится после придаточного предложения времени с составным союзом 'по мере того как'."
    },
    {
        'sentence': "Он почувствовал раздражение и чтобы не сказать лишнего быстро встал и пошёл в дом",
        'correct': "Он почувствовал раздражение и, чтобы не сказать лишнего, быстро встал и пошёл в дом.",
        'explanation': "Запятыми выделяется придаточное цели с союзом 'чтобы', запятая перед союзом 'и' не ставится, так как он соединяет однородные сказуемые."
    },
    {
        'sentence': "Мы свернули налево думая что может быть хоть на этом проселке есть какое-нибудь жилье",
        'correct': "Мы свернули налево, думая, что, может быть, хоть на этом проселке есть какое-нибудь жилье.",
        'explanation': "Запятыми выделяется деепричастный оборот, вводное сочетание 'может быть' и ставится запятая перед союзом 'что'."
    },
    {
        'sentence': "В душе моей было такое ощущение как будто распустился свежий благоухающий цветок",
        'correct': "В душе моей было такое ощущение, как будто распустился свежий благоухающий цветок.",
        'explanation': "Запятая ставится перед составным союзом 'как будто' в сложноподчинённом предложении."
    },
    {
        'sentence': "Маленькие ничтожные ручейки превратились теперь в бурные многоводные потоки переправа через которые отняла у нас много времени",
        'correct': "Маленькие ничтожные ручейки превратились теперь в бурные многоводные потоки, переправа через которые отняла у нас много времени.",
        'explanation': "Запятая ставится перед придаточным определительным с союзным словом 'которые'."
    },
    # Сложные предложения с разными видами подчинения
    {
        'sentence': "Жизнь каждого человека принадлежит отечеству и не удальство а только истинная храбрость приносит пользу",
        'correct': "Жизнь каждого человека принадлежит отечеству, и не удальство, а только истинная храбрость приносит пользу.",
        'explanation': "Запятая ставится перед союзом 'и', соединяющим части сложного предложения, и перед противительным союзом 'а'."
    },
    {
        'sentence': "Уж много лет не бывал я на своей родине и каждое новое посещение наполняет моё сердце радостью и печалью",
        'correct': "Уж много лет не бывал я на своей родине, и каждое новое посещение наполняет моё сердце радостью и печалью.",
        'explanation': "Запятая ставится перед союзом 'и', соединяющим части сложносочинённого предложения. Перед вторым 'и' запятая не ставится, так как он соединяет однородные члены."
    },
    {
        'sentence': "Тёмными мокрыми ночами с шумом томительно и тяжко оседал подтаявший снег и в лесу что-то звонко лопалось с протяжным ликующим звуком",
        'correct': "Тёмными мокрыми ночами с шумом томительно и тяжко оседал подтаявший снег, и в лесу что-то звонко лопалось с протяжным ликующим звуком.",
        'explanation': "Запятая ставится перед союзом 'и', соединяющим части сложносочинённого предложения. Однородные определения 'тёмными мокрыми' не разделяются запятой, так как характеризуют предмет с одной стороны."
    },
    {
        'sentence': "Вставало безоблачное небо и очень быстро светлело",
        'correct': "Вставало безоблачное небо, и очень быстро светлело.",
        'explanation': "Запятая ставится перед союзом 'и', соединяющим части сложносочинённого предложения с разными грамматическими основами."
    },
    {
        'sentence': "Тем временем распогодилось и небо над головой посветлело зарумянилось",
        'correct': "Тем временем распогодилось, и небо над головой посветлело, зарумянилось.",
        'explanation': "Запятая ставится перед союзом 'и' и между однородными сказуемыми 'посветлело, зарумянилось'."
    },

    # Предложения с обособленными оборотами и уточнениями
    {
        'sentence': "Льётся тёплый солнечный воздух в комнаты шумят воробьи на сирени",
        'correct': "Льётся тёплый солнечный воздух в комнаты, шумят воробьи на сирени.",
        'explanation': "Запятая разделяет части бессоюзного сложного предложения, где перечисляются одновременные события."
    },
    {
        'sentence': "К солнцу потянулись нежные ростки трав тайга обновилась заполнилась голосами певчих птиц",
        'correct': "К солнцу потянулись нежные ростки трав, тайга обновилась, заполнилась голосами певчих птиц.",
        'explanation': "Запятые разделяют части бессоюзного сложного предложения и однородные сказуемые."
    },
    {
        'sentence': "На улице было ещё пусто над крышами домов вставало солнце",
        'correct': "На улице было ещё пусто, над крышами домов вставало солнце.",
        'explanation': "Запятая разделяет части бессоюзного сложного предложения, где вторая часть дополняет первую."
    },
    {
        'sentence': "Занималась заря от воды поднимался густой туман было холодно и сыро",
        'correct': "Занималась заря, от воды поднимался густой туман, было холодно и сыро.",
        'explanation': "Запятые разделяют части бессоюзного сложного предложения. Союз 'и' соединяет однородные сказуемые."
    },
    {
        'sentence': "Лес горы слились всё окуталось густым туманом",
        'correct': "Лес, горы слились, всё окуталось густым туманом.",
        'explanation': "Запятая ставится между однородными подлежащими и частями бессоюзного сложного предложения."
    },
    # Предложения с разными видами связи и сложной пунктуацией
    {
        'sentence': "Травостой выдался небывалый никогда ещё по уверению стариков здесь не видели ни такого клевера ни такой люцерны ни столь густого и сочного разнотравья",
        'correct': "Травостой выдался небывалый: никогда ещё, по уверению стариков, здесь не видели ни такого клевера, ни такой люцерны, ни столь густого и сочного разнотравья.",
        'explanation': "Двоеточие ставится для пояснения, запятыми выделяется вводная конструкция, запятые разделяют однородные члены с повторяющимся союзом 'ни'."
    },
    {
        'sentence': "Туман казался неподвижным и сонным травы и кусты были мокрые",
        'correct': "Туман казался неподвижным и сонным, травы и кусты были мокрые.",
        'explanation': "Запятая разделяет части сложносочиненного предложения. Союз 'и' соединяет однородные определения и однородные подлежащие."
    },
    {
        'sentence': "Черная во всё небо туча надвигалась на нашу стоянку с севера приближался буран",
        'correct': "Черная, во всё небо, туча надвигалась на нашу стоянку с севера, приближался буран.",
        'explanation': "Запятыми выделяется уточняющий оборот 'во всё небо', запятая разделяет части бессоюзного сложного предложения."
    },
    {
        'sentence': "Рожь гнулась и качалась на нивах лес синевший впереди побледнел расплылся и исчез по полям шумно стремились к нам навстречу колеблющиеся столбы ливня",
        'correct': "Рожь гнулась и качалась на нивах, лес, синевший впереди, побледнел, расплылся и исчез, по полям шумно стремились к нам навстречу колеблющиеся столбы ливня.",
        'explanation': "Запятыми выделяется причастный оборот, разделяются части бессоюзного предложения и однородные сказуемые."
    },
    {
        'sentence': "Небо чистое и звёздное всю ночь затянуло вода слегка курилась в какой-то тусклой белёсости наступало утро",
        'correct': "Небо, чистое и звёздное, всю ночь затянуло, вода слегка курилась в какой-то тусклой белёсости, наступало утро.",
        'explanation': "Запятыми выделяются однородные определения, разделяются части бессоюзного сложного предложения."
    },

    # Предложения с различными синтаксическими конструкциями
    {
        'sentence': "За холмом глухо прогремел гром подуло свежестью",
        'correct': "За холмом глухо прогремел гром, подуло свежестью.",
        'explanation': "Запятая разделяет части бессоюзного сложного предложения, где второе предложение безличное."
    },
    {
        'sentence': "Иван Иванович бреет бороду в неделю два раза Иван Никифорович один раз",
        'correct': "Иван Иванович бреет бороду в неделю два раза, Иван Никифорович – один раз.",
        'explanation': "Запятая разделяет части бессоюзного сложного предложения, тире ставится на месте пропущенного сказуемого."
    },
    {
        'sentence': "Нет счастья без родины каждый пускает корни в родную землю",
        'correct': "Нет счастья без родины: каждый пускает корни в родную землю.",
        'explanation': "Двоеточие ставится, так как вторая часть поясняет смысл первой части бессоюзного предложения."
    },
    {
        'sentence': "Месяц над нашею крышей светит вечер стоит у двора",
        'correct': "Месяц над нашею крышей светит, вечер стоит у двора.",
        'explanation': "Запятая разделяет части бессоюзного сложного предложения, где перечисляются одновременные события."
    },
    {
        'sentence': "У огня сидел Дерсу вид у него был изнурённый усталый",
        'correct': "У огня сидел Дерсу, вид у него был изнурённый, усталый.",
        'explanation': "Запятая разделяет части бессоюзного сложного предложения и однородные определения."
    }

]

# Бдшка
BD = [
    # Задания типа 1 (A, B, C, D)
    {
        'id': 1,
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
        'id': 2,
        'image': r'/home/KrE3st/bot/Задания/Задания 1/1.2.png',
        'correct': 'B',
        'type': 'type1',
        'keyboard': kb_type1,
        'explanation': '''Запятая 1 отделяет части сложносочиненного предложения.
Запятые 3 и 4 выделяют придаточное предложение «чтобы ощутить их нежную бархатистость».
Запятые должны стоять на местах 1, 3 и 4.'''
    },
    {
        'id': 3,
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
        'id': 4,
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
        'id': 5,
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
        'id': 6,
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
        'id': 7,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.1.png',
        'correct': 'B',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''Если пойдёт дождь, мы останемся дома, а если будет солнечно, пойдём гулять.
Здесь две придаточные части равноправны и соединены союзом «а». Они обе отвечают на один и тот же вопрос главного предложения («Что произойдёт, если...»), имеют одинаковую грамматическую форму и структуру — значит, подчинение параллельное.
'''
    },
    {
        'id': 8,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.2.png',
        'correct': 'C',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''Я знаю, что он приедет, и что привезёт подарок.
Первое придаточное («что он приедет») относится к главному предложению, второе («что привезёт подарок») зависит от первого придаточного. Подчинительные отношения идут последовательно одно за другим.
'''
    },
    {
        'id': 9,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.3.png',
        'correct': 'B',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''Я думаю, что он сдаст экзамен, потому что хорошо подготовился.
Придаточные части («что он сдаст экзамен», «потому что хорошо подготовился») зависят от одного и того же главного предложения и находятся в отношениях причины и следствия, оба отвечают на вопросы одного типа («Почему я так думаю?»). Это именно однородное подчинение.
'''
    },
    {
        'id': 10,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.4.png',
        'correct': 'A',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''
        Последовательное подчинение подразумевает зависимость второй придаточной части от первой.'''
    },
    {
        'id': 11,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.5.png',
        'correct': 'C',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''Он сказал, что сдаст экзамен и что будет поступать в университет.
Здесь второе придаточное («что будет поступать в университет») связано с первым («что сдаст экзамен»), а само первое связано с главным («он сказал»). Получилась цепочка подчинения, то есть последовательное подчинение.
'''
    },
    {
        'id': 12,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.6.png',
        'correct': 'B',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''Эти придаточные относятся к главному предложению («Мы пошли в парк») независимо друг от друга и не выстраиваются в цепочку, где одно придаточное зависело бы от другого. Соответственно, придаточные части соединяются параллельно.
        '''
    },
    # Задания типа 3 (Правда/Ложь)
    {
        'id': 13,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.1.png',
        'correct': 'true',
        'type': 'type3',
        'keyboard': kb_type3,
        'explanation': '''Части сложносочинённого предложения (ССП) равноправны, и между ними действительно можно поставить точку, если они выражают законченную мысль и могут существовать как отдельные предложения.
        '''
    },
    {
        'id': 14,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.2.png',
        'correct': 'true',
        'type': 'type3',
        'keyboard': kb_type3,
        'explanation': '''В сложноподчинённом предложении (СПП) может быть последовательное подчинение придаточных. Это значит, что одно придаточное подчиняется главному, а другое — первому придаточному, и так далее — выстраивается "цепочка" подчинения.
        '''
    },
    {
        'id': 15,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.3.png',
        'correct': 'false',
        'type': 'type3',
        'keyboard': kb_type3,
        'explanation': '''В сложноподчинённом предложении (СПП) может быть последовательное подчинение придаточных. Это значит, что одно придаточное подчиняется главному, а другое — первому придаточному, и так далее — выстраивается "цепочка" подчинения.
        '''
    },
    {
        'id': 16,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.4.png',
        'correct': 'false',
        'type': 'type3',
        'keyboard': kb_type3,
        'explanation': '''В сложноподчинённом предложении главная часть может стоять как до, так и после придаточной.
        '''
    },
    {
        'id': 17,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.5.png',
        'correct': 'true',
        'type': 'type3',
        'keyboard': kb_type3,
        'explanation': '''Утверждение «Придаточные части в сложноподчинённом предложении могут быть однородными» — верно.
        '''
    },
    {
        'id': 18,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.6.png',
        'correct': 'true',
        'type': 'type3',
        'keyboard': kb_type3,
        'explanation': '''Утверждение «В бессоюзном сложном предложении нет союзов, связывающих части» — верно.
        '''
    },
    # Задания типа 4 (ЕГЭ)
    {
        'id': 19,
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
        'id': 20,
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
        'id': 23,
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
        'id': 24,
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
        'id': 25,
        'image': r'/home/KrE3st/bot/Задания/Задания 1/1.7.png',
        'correct': 'C',
        'type': 'type1',
        'keyboard': kb_type1,
        'explanation': '''Запятые под номерами 2, 4 выделяют однородные придаточные предложения 2 и 3. Они отвечают на один вопрос и относятся к главному 1: направился когда?

Запятые должны стоять на местах 2, 4.
        '''
    },
    {
        'id': 26,
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
        'id': 27,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.7.png',
        'correct': 'C',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''Придаточные отвечают на один и тот же вопрос («какие?») и относятся к одному и тому же слову в главной части («дни»).
        '''
    },
    {
        'id': 28,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.8.png',
        'correct': 'C',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''Оба придаточных относятся к одному главному предложению.
        '''
    },
    {
        'id': 29,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.9.png',
        'correct': 'C',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''Придаточные связаны с главным предложением и отвечают на один и тот же вопрос («чему?»).
        '''
    },
    {
        'id': 30,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.10.png',
        'correct': 'C',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''Придаточные связаны с главным предложением и связаны сочинительными союзами либо бессоюзно.
        '''
    },
    {
        'id': 31,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.7.png',
        'correct': 'true',
        'type': 'type3',
        'keyboard': kb_type3,
        'explanation': '''Это объясняется их равноправностью: простые предложения в составе сложного возможно разделить на простые, смысл их не потеряется.
        '''
    },
    {
        'id': 32,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.8.png',
        'correct': 'true',
        'type': 'type3',
        'keyboard': kb_type3,
    },
    {
        'id': 33,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.9.png',
        'correct': 'true',
        'type': 'type3',
        'keyboard': kb_type3,
        'explanation': '''Этим БСП отличаются от сложносочинённых и сложноподчинённых предложений, в которых данную роль выполняют союзы.
        '''
    },
    {
        'id': 34,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.10.png',
        'correct': 'true',
        'type': 'type3',
        'keyboard': kb_type3,
        'explanation': '''Тире следует поставить в том случае, если вторая часть сложносочинённого предложения содержит в себе результат, следствие либо резко противопоставлена первой части.
        '''
    },
    {
        'id': 35,
        'image': r'/home/KrE3st/bot/Задания/Задания 1/1.8.png',
        'correct': 'A',
        'type': 'type1',
        'keyboard': kb_type1,
        'explanation': '''Запятая под номером 1 отделяет части, связанные сочинительной связью: «Рита сильно расстроилась из-за отъезда отца» и « но ... девочка быстро утешилась и перестала плакать». Запятые под номерами 2 и 3 выделяют придаточное предложение «когда он пообещал привезти ей из плавания настоящего большого попугая». Запятые под номерами 3 и 4 выделяют придаточное предложение «какого они видели недавно в зоопарке».

Запятые должны стоять на местах 1, 2, 3 и 4.
        '''
    },
    {
        'id': 36,
        'image': r'/home/KrE3st/bot/Задания/Задания 1/1.9.png',
        'correct': 'D',
        'type': 'type1',
        'keyboard': kb_type1,
        'explanation': '''Запятая под номером 1 отделяет части, связанные подчинительной связью: «Илья Андреевич понимал» и «что (2) если не собрать яблоки до наступления холодов». Запятая под номером 3 отделяет части, связанные подчинительной связью: «(2) если не собрать яблоки до наступления холодов» и «то весь урожай погибнет», запятая под номером 4 отделяет части, связанные сочинительной связью: «Илья Андреевич понимал» и «но обстоятельства не позволяли ему оставить работу и уехать в деревню даже на несколько дней».

Ответ:134
        '''
    },
    {
        'id': 37,
        'image': r'/home/KrE3st/bot/Задания/Задания 1/1.10.png',
        'correct': 'B',
        'type': 'type1',
        'keyboard': kb_type1,
        'explanation': '''На стыке союзов или союзов и союзных слов (и хотя, но когда, и если; что когда, что куда, который если и др.) запятая ставится тогда, когда после придаточной части нет союза но или второй части двойного союза  — то или так. Это как раз наш случай.

Запятые должны стоять на местах 1, 2, 3 и 4.
        '''
    },
    {
        'id': 38,
        'image': r'/home/KrE3st/bot/Задания/Задания 4/4.8.png',
        'correct': '145',
        'type': 'type4',
        'instruction': 'Напишите ответ цифрами в порядке возрастания',
        'explanation': '''Запятая на месте цифры 1 ставится, так как начинается придаточная часть при звуках трескучего голоса которого Артём… даже остановил работу. Союзное слово который в этой придаточной оттянуто в середину предложения (границы придаточной части легко определить, если заменить относительное местоимение который на соответствующее ему существительное господин из предыдущей части). Запятые на месте цифр 2 и 3 не ставятся.
Запятые на месте 4 и 5 ставятся, так как они выделяют ещё одну придаточную часть чтобы посмеяться всласть, которая находится внутри предыдущей придаточной.'''
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
    {
        'id': 41,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.11.png',
        'correct': 'C',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''В предложении "Я знал, что мне предстоит трудный путь, что впереди много испытаний" придаточные предложения "что мне предстоит трудный путь" и "что впереди много испытаний" отвечают на один и тот же вопрос (что?), относятся к одному слову в главной части (знал) и связаны сочинительным союзом "и". Это однородное подчинение.'''
    },
    {
        'id': 42,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.12.png',
        'correct': 'A',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''В предложении "Когда наступила весна, которую все так долго ждали, природа начала оживать" придаточное "которую все так долго ждали" зависит от слова "весна" из первого придаточного "когда наступила весна". Это последовательное подчинение.'''
    },
    {
        'id': 43,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.13.png',
        'correct': 'B',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''В предложении "Если пойдет дождь, хотя синоптики этого не обещали, мы останемся дома" придаточные предложения "если пойдет дождь" и "хотя синоптики этого не обещали" относятся к главному предложению "мы останемся дома", но отвечают на разные вопросы (при каком условии? несмотря на что?). Это параллельное подчинение.'''
    },
    {
        'id': 44,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.14.png',
        'correct': 'A',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''В предложении "Учитель объяснил, что задача решается легко, если применить нужную формулу" придаточное "если применить нужную формулу" зависит от придаточного "что задача решается легко", которое в свою очередь зависит от главного предложения. Это последовательное подчинение.'''
    },
    {
        'id': 45,
        'image': r'/home/KrE3st/bot/Задания/Задания 2/2.15.png',
        'correct': 'C',
        'type': 'type2',
        'keyboard': kb_type2,
        'explanation': '''В предложении "Мне сказали, что встреча переносится и что нужно предупредить всех участников" оба придаточных отвечают на один вопрос (что?), относятся к одному слову в главной части (сказали) и соединены сочинительным союзом "и". Это однородное подчинение.'''
    },
    {
        'id': 46,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.11.png',
        'correct': 'true',
        'type': 'type3',
        'keyboard': kb_type3,
        'explanation': '''Это утверждение верно. При однородном подчинении придаточные части отвечают на один и тот же вопрос, относятся к одному и тому же слову в главной части и связаны между собой сочинительной связью (союзами и, или, либо и др.). Например: "Я понял, что опоздал и что встреча уже закончилась".'''
    },
    {
        'id': 47,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.12.png',
        'correct': 'false',
        'type': 'type3',
        'keyboard': kb_type3,
        'explanation': '''Это утверждение неверно. При последовательном подчинении придаточные предложения образуют цепочку, где первое придаточное зависит от главного, второе – от первого придаточного, третье – от второго и т.д. Например: "Я знаю (главное), что он сказал (1-е придаточное), когда вернется домой (2-е придаточное)".'''
    },
    {
        'id': 48,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.13.png',
        'correct': 'true',
        'type': 'type3',
        'keyboard': kb_type3,
        'explanation': '''Это утверждение верно. При параллельном подчинении все придаточные части относятся к одному и тому же слову в главной части или ко всей главной части, но отвечают на разные вопросы. Например: "Когда взошло солнце (придаточное времени), мы отправились в путь, хотя погода была пасмурной (придаточное уступки)".'''
    },
    {
        'id': 49,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.14.png',
        'correct': 'false',
        'type': 'type3',
        'keyboard': kb_type3,
        'explanation': '''Это утверждение неверно. В сложноподчинённом предложении с последовательным подчинением может быть два и более придаточных, образующих цепочку зависимостей. Количество придаточных не ограничено двумя. Например: "Я думаю (главное), что он знает (1-е придаточное), где находится место (2-е придаточное), куда мы должны прийти (3-е придаточное)".'''
    },
    {
        'id': 50,
        'image': r'/home/KrE3st/bot/Задания/Задания 3/3.15.png',
        'correct': 'true',
        'type': 'type3',
        'keyboard': kb_type3,
        'explanation': '''Это утверждение верно. В одном сложном предложении могут сочетаться разные виды подчинения. Например: "Когда начался дождь (1-е придаточное), я вспомнил, что забыл зонт (2-е придаточное) и что придется промокнуть (3-е придаточное)". Здесь сочетаются параллельное подчинение (первое придаточное) и однородное подчинение (второе и третье придаточные).'''
    },
    {
        'id': 51,
        'image': r'/home/KrE3st/bot/Задания/Задания 1/1.11.png',
        'correct': 'A',
        'type': 'type1',
        'keyboard': kb_type1,
        'explanation': '''Запятые 1,2 выделяют деепричастный оборот "пробившись сквозь кровлю деревьев". Запятые 4,5 выделяют причастный оборот "окутанный этим серебристым светом". Запятая 3 не нужна, так как союз "и" соединяет однородные сказуемые.'''
    },

    {
        'id': 52,
        'image': r'/home/KrE3st/bot/Задания/Задания 1/1.12.png',
        'correct': 'C',
        'type': 'type1',
        'keyboard': kb_type1,
        'explanation': '''Запятая 1 ставится между частями бессоюзного сложного предложения. Запятая 2 - перед подчинительным союзом "как". Запятая 3 ставится после причастного оборота. Запятая 4 не нужна, так как "вдруг" не является вводным словом.'''
    },

    {
        'id': 53,
        'image': r'/home/KrE3st/bot/Задания/Задания 1/1.13.png',
        'correct': 'B',
        'type': 'type1',
        'keyboard': kb_type1,
        'explanation': '''Запятая 1 ставится между частями бессоюзного сложного предложения. Запятая 2 ставится между частями сложного предложения перед союзом "и", который соединяет последние две части предложения.'''
    },

    {
        'id': 54,
        'image': r'/home/KrE3st/bot/Задания/Задания 1/1.14.png',
        'correct': 'D',
        'type': 'type1',
        'keyboard': kb_type1,
        'explanation': '''Запятая 1 ставится между частями бессоюзного сложного предложения. Запятая 2 ставится между частями сложного предложения перед союзом "и", так как он соединяет части сложного предложения.'''
    },

    {
        'id': 55,
        'image': r'/home/KrE3st/bot/Задания/Задания 1/1.15.png',
        'correct': 'A',
        'type': 'type1',
        'keyboard': kb_type1,
        'explanation': '''Запятые 1 и 2 ставятся между частями бессоюзного сложного предложения. Запятая 3 ставится перед противительным союзом "а".'''
    },
    {
        'id': 56,
        'image': r'/home/KrE3st/bot/Задания/Задания 4/4.11.png',
        'correct': '123',
        'type': 'type4',
        'instruction': 'Напишите ответ цифрами в порядке возрастания',
        'explanation': '''Запятые на месте цифр 1, 2 ,3  отделяют придаточные части от главной части и друг от друга.
Запятые на месте 4 и 5 не ставятся, потому что союзное слово в этой придаточной части оттянуто в середину предложения, но границы придаточного легко определить, если заменить относительное местоимение который соответствующим ему существительным свойство.'''
    },
    {
        'id': 57,
        'image': r'/home/KrE3st/bot/Задания/Задания 4/4.12.png',
        'correct': '125',
        'type': 'type4',
        'instruction': 'Напишите ответ цифрами в порядке возрастания',
        'explanation': '''На месте цифр 1 и 2 ставятся запятые, потому что они выделяют придаточную часть коренная причина которого заключается в бесконечных изменениях взаимодействия исторических сил, которая разрывает главную часть [В этом разнообразии… самое важное есть то].
На месте цифр 3 и 4 запятые не ставятся, так как союзное слово который оттянуто в середину придаточной части (отсутствие запятых легко обосновать, если заменить местоимение который на соответствующее ему имя существительное из главной части предложения: разнообразие).
Запятая на месте цифры 5 ставится, поскольку она отделяет новую придаточную часть что элементы общежития в различных сочетаниях и положениях обнаруживают неодинаковые свойства и действия от главной.'''
    },
    {
        'id': 58,
        'image': r'/home/KrE3st/bot/Задания/Задания 4/4.13.png',
        'correct': '124',
        'type': 'type4',
        'instruction': 'Напишите ответ цифрами в порядке возрастания',
        'explanation': '''На месте цифры 1 ставится запятая, отделяющая придаточное предложение с союзом КОГДА от главного.
На месте цифры 2 запятая ставится перед придаточным предложением с союзом ЧТО.
На месте цифры 4 запятая ставится перед придаточным определительным. Союзное слово «которой» стоит не в начале, а в середине придаточного определительного предложения, поэтому запятая ставится не перед словом «которой», а перед словами «во время».'''
    },
    {
        'id': 59,
        'image': r'/home/KrE3st/bot/Задания/Задания 4/4.14.png',
        'correct': '125',
        'type': 'type4',
        'instruction': 'Напишите ответ цифрами в порядке возрастания',
        'explanation': '''Перед союзом КАК ставится запятая (цифра 1), отделяющая придаточное изъяснительное предложение от главного.
Союзное слово «которых» стоит не в начале, а в середине придаточного определительного предложения, поэтому запятая ставится не перед словом «которых», а перед словом «цепь» (цифра 2).
После определительного придаточного следует придаточное степени с союзом «что» (цифра 5).'''
    },
    {
        'id': 60,
        'image': r'/home/KrE3st/bot/Задания/Задания 4/4.15.png',
        'correct': '14',
        'type': 'type4',
        'instruction': 'Напишите ответ цифрами в порядке возрастания',
        'explanation': '''Союзное слово «на которую» стоит не в начале, а в середине придаточного определительного предложения, поэтому запятая ставится перед словом «взобраться» (цифра 1). После определительного придаточного следует придаточное причины с союзом «поскольку» (цифра 4).'''
    },
    {
        'id': 61,
        'image': r'/home/KrE3st/bot/Задания/Задания 5/5.1.png',  # схема: [  ], (что), (если), (который)
        'sentences': [
            "A) Я понимал что если погода наладится мы отправимся в поход который давно планировали.",
            "B) Я точно знал что если он придёт вовремя мы успеем закончить проект который давно откладывали.",
            "C) Я думаю что когда он вернётся мы обсудим вопрос который всех волнует."
        ],
        'correct': 'B',
        'type': 'type5',
        'keyboard': kb_type2,  # используем клавиатуру с кнопками A, B, C
        'explanation': '''Схема соответствует варианту B, так как это сложноподчинённое предложение с последовательным подчинением: главное предложение "Я точно знал" подчиняет придаточное изъяснительное (что), внутри которого находится придаточное условия (если), а также есть придаточное определительное (который). В варианте A похожая структура, но другой порядок частей, а в варианте C вместо условия используется придаточное времени.'''
    },

    {
        'id': 62,
        'image': r'/home/KrE3st/bot/Задания/Задания 5/5.2.png',  # схема: (Несмотря на то что), [  ]
        'sentences': [
            "A) В то время как солнце садилось туман начал рассеиваться.",
            "B) По мере того как мы поднимались воздух становился прохладнее.",
            "C) Несмотря на то что было холодно снег таял совсем незаметно."
        ],
        'correct': 'C',
        'type': 'type5',
        'keyboard': kb_type2,
        'explanation': '''Схема соответствует варианту C, так как содержит придаточное уступки с составным союзом "несмотря на то что" в начале предложения. Варианты A и B имеют похожую структуру, но используют другие составные союзы и выражают временные отношения.'''
    },

    {
        'id': 63,
        'image': r'/home/KrE3st/bot/Задания/Задания 5/5.3.png',  # схема: [  ], (как), (будто)
        'sentences': [
            "A) Он заговорил так же внезапно как вошёл мгновенно сделав вид будто не заметил моей потерянности.",
            "B) Он говорил так тихо как говорят люди делая вид будто это неважно.",
            "C) Он смотрел так пристально как смотрят когда хотят что-то запомнить."
        ],
        'correct': 'A',
        'type': 'type5',
        'keyboard': kb_type2,
        'explanation': '''Схема соответствует варианту A, так как содержит последовательное подчинение с придаточным сравнительным (как) и придаточным сравнительным (будто). Вариант B похож по структуре, но имеет другой порядок частей, а в варианте C вместо придаточного с "будто" используется придаточное времени.'''
    },

    {
        'id': 64,
        'image': r'/home/KrE3st/bot/Задания/Задания 5/5.4.png',  # схема: [  ], (чтобы), [  ]
        'sentences': [
            "A) Он почувствовал раздражение и чтобы не сказать лишнего быстро встал и пошёл в дом.",
            "B) Он остановился и чтобы перевести дыхание прислонился к стене и закрыл глаза.",
            "C) Он замолчал и чтобы скрыть волнение отвернулся к окну."
        ],
        'correct': 'A',
        'type': 'type5',
        'keyboard': kb_type2,
        'explanation': '''Схема соответствует варианту A, так как содержит придаточное цели (чтобы) между двумя частями главного предложения, соединенными союзом "и". Все три варианта похожи по структуре, но только в варианте A есть два однородных сказуемых после придаточного предложения.'''
    },

    {
        'id': 65,
        'image': r'/home/KrE3st/bot/Задания/Задания 5/5.5.png',  # схема: [  ], (как только), [  ]
        'sentences': [
            "A) Вечером как только стемнело в домах зажглись огни.",
            "B) Вечером как только темнота скрыла море пассажиры разошлись по каютам.",
            "C) Утром как только рассвело птицы начали свой концерт."
        ],
        'correct': 'B',
        'type': 'type5',
        'keyboard': kb_type2,
        'explanation': '''Схема соответствует варианту B, так как это сложноподчинённое предложение с придаточным времени (как только), где в главной части есть составное именное сказуемое. Все варианты похожи по структуре, но различаются наличием второстепенных членов и типом сказуемого в главной части.'''
    },
    {
        'id': 66,
        'image': r'/home/KrE3st/bot/Задания/Задания 5/5.6.png',  # схема: [  ], (если), (то)
        'sentences': [
            "A) Я приду и если вы чего-нибудь не поняли объясню.",
            "B) Если пойдёт дождь то мы останемся дома и будем читать книги.",
            "C) Когда выпадет снег то дети пойдут кататься на санках."
        ],
        'correct': 'B',
        'type': 'type5',
        'keyboard': kb_type2,
        'explanation': '''Схема соответствует варианту B, так как это сложноподчинённое предложение с придаточным условия, где используется двойной союз "если..., то". В варианте A нет второй части союза "то", а в варианте C используется союз "когда" вместо "если".'''
    },

    {
        'id': 67,
        'image': r'/home/KrE3st/bot/Задания/Задания 5/5.7.png',  # схема: [  ], (и когда), [  ]
        'sentences': [
            "A) Солнце медленно сползает с неба на край степи и когда оно почти касается земли становится багровым.",
            "B) Я пошёл быстро почти побежал и когда очутился на окраине тихой деревушки перевёл дух.",
            "C) Родители провожали детей на отдых и когда поезд тронулся долго махали им вслед."
        ],
        'correct': 'A',
        'type': 'type5',
        'keyboard': kb_type2,
        'explanation': '''Схема соответствует варианту A, так как содержит главное предложение, разорванное придаточным времени с союзом "и когда". В варианте B и C похожая структура, но другое расположение частей предложения.'''
    },

    {
        'id': 68,
        'image': r'/home/KrE3st/bot/Задания/Задания 5/5.8.png',  # схема: (По мере того как), [  ]
        'sentences': [
            "A) В то время как мы собирались в поход погода начала портиться.",
            "B) По мере того как мы отходили от водораздела долина суживалась всё более и более.",
            "C) С тех пор как он вернулся в город многое изменилось."
        ],
        'correct': 'B',
        'type': 'type5',
        'keyboard': kb_type2,
        'explanation': '''Схема соответствует варианту B, так как содержит придаточное времени с составным союзом "по мере того как" в начале предложения. В вариантах A и C используются другие составные союзы.'''
    },

    {
        'id': 69,
        'image': r'/home/KrE3st/bot/Задания/Задания 5/5.9.png',  # схема: [  ], (что), (чтобы)
        'sentences': [
            "A) С веками всё меньше становится даровых благ на земле и чтобы не знать горя впереди надо разумно тратить всякую копейку.",
            "B) Дети знают что такое благодарность и умеют сохранять её надолго.",
            "C) Я знаю что нужно сделать чтобы решить эту проблему."
        ],
        'correct': 'C',
        'type': 'type5',
        'keyboard': kb_type2,
        'explanation': '''Схема соответствует варианту C, так как содержит последовательное подчинение: сначала придаточное изъяснительное (что), затем придаточное цели (чтобы). В варианте A придаточное цели не зависит от придаточного изъяснительного, а в варианте B нет придаточного цели.'''
    },

    {
        'id': 70,
        'image': r'/home/KrE3st/bot/Задания/Задания 5/5.10.png',  # схема: [  ], (что), (где)
        'sentences': [
            "A) Я не понимал в чём причина нашей неудачи и ощущал упадок сил.",
            "B) Он сказал что знает где находится нужный нам дом.",
            "C) Мы думали что сможем когда захотим вернуться обратно."
        ],
        'correct': 'B',
        'type': 'type5',
        'keyboard': kb_type2,
        'explanation': '''Схема соответствует варианту B, так как содержит последовательное подчинение с придаточным изъяснительным (что) и придаточным места (где). В варианте A другой тип придаточного, а в варианте C придаточное времени вместо места.'''
    },
    {
        'id': 71,
        'image': r'/home/KrE3st/bot/Задания/Задания 5/5.11.png',  # схема: [  ], (хотя), (но)
        'sentences': [
            "A) Как бы ни было уныло и неприветливо покинутое место всегда остаётся в душе сожаление.",
            "B) Двор Ивана Никифоровича хотя был возле двора Ивана Ивановича и можно было перелезть из одного в другой через плетень однако ж Иван Иванович пошёл улицею.",
            "C) Хотя было холодно снег таял совсем незаметно."
        ],
        'correct': 'B',
        'type': 'type5',
        'keyboard': kb_type2,
        'explanation': '''Схема соответствует варианту B, так как содержит придаточное уступки с союзом "хотя" и противительный союз "однако ж" (синоним "но") в главной части. В варианте A другая структура с уступительным придаточным, а в варианте C отсутствует противительный союз.'''
    },

    {
        'id': 72,
        'image': r'/home/KrE3st/bot/Задания/Задания 5/5.12.png',  # схема: [  ], (пока), (и)
        'sentences': [
            "A) Я сижу рядом с рыболовом и пока мы разговариваем ему попадается несколько славных рыбин.",
            "B) Пока я осматривал окрестность палатки были поставлены и ужин приготовлен.",
            "C) Мы сидели у костра и когда стемнело начали собираться домой."
        ],
        'correct': 'A',
        'type': 'type5',
        'keyboard': kb_type2,
        'explanation': '''Схема соответствует варианту A, так как содержит главное предложение, придаточное времени с союзом "пока" и соединительный союз "и". В варианте B придаточное стоит в начале, а в варианте C используется союз "когда" вместо "пока".'''
    },

    {
        'id': 73,
        'image': r'/home/KrE3st/bot/Задания/Задания 5/5.13.png',  # схема: [  ], (который), (где)
        'sentences': [
            "A) Сказки отца от которых быть может пошла моя страсть к путешествиям распаляли воображение.",
            "B) В комнате стояли серые сумерки сквозь которые ясно вырисовывались печка и спящая девочка.",
            "C) Передо мной было большое круглое болото занесённое снегом из-под белой пелены которого торчали редкие кочки где прятались птицы."
        ],
        'correct': 'C',
        'type': 'type5',
        'keyboard': kb_type2,
        'explanation': '''Схема соответствует варианту C, так как содержит последовательное подчинение: сначала определительное придаточное с союзным словом "который", затем придаточное места с союзным словом "где". В вариантах A и B только одно придаточное предложение.'''
    },

    {
        'id': 74,
        'image': r'/home/KrE3st/bot/Задания/Задания 5/5.14.png',  # схема: [  ], (и), (что)
        'sentences': [
            "A) Накинув на плечо одностволку он подвинулся ближе к костру и наблюдая как пламя пожирает головёшки погрузился в свои думы.",
            "B) Его богатая энергия постоянно ищет выхода и когда нет ей применения в делах она разряжается по пустякам.",
            "C) Животные наверняка видели как мы ломали ветки и вероятно слышали что мы громко разговаривали."
        ],
        'correct': 'C',
        'type': 'type5',
        'keyboard': kb_type2,
        'explanation': '''Схема соответствует варианту C, так как содержит два однородных сказуемых, соединенных союзом "и", при которых есть придаточные изъяснительные с союзами "как" и "что". В варианте A деепричастный оборот, а в варианте B придаточное времени.'''
    },

    {
        'id': 75,
        'image': r'/home/KrE3st/bot/Задания/Задания 5/5.15.png',  # схема: (По мере того как), [  ], (и)
        'sentences': [
            "A) По мере того как мы отходили от водораздела долина суживалась всё более и более и наконец превратилась в глубокое ущелье.",
            "B) В то время как солнце садилось туман начал рассеиваться и птицы затихли.",
            "C) Когда наступил вечер небо заволокло тучами и пошёл дождь."
        ],
        'correct': 'A',
        'type': 'type5',
        'keyboard': kb_type2,
        'explanation': '''Схема соответствует варианту A, так как содержит придаточное времени с составным союзом "по мере того как" в начале предложения, за которым следует главное предложение с однородными сказуемыми, соединенными союзом "и". В вариантах B и C используются другие временные союзы.'''
    },
    {
        'id': 76,
        'image': r'/home/KrE3st/bot/Задания/Задания 6/6.1.png',  # схема: [  ], (если), (то), (который)
        'start_text': "Мы обязательно купим дом...",
        'sentences': [
            "A) если будет возможность то который находится рядом с парком",
            "B) если будет возможность то мы купим дом который находится рядом с парком",
            "C) который находится рядом с парком если будет возможность то купим"
        ],
        'correct': 'B',
        'type': 'type6',
        'keyboard': kb_type2,
        'explanation': '''По схеме требуется: условное придаточное (если), вторая часть двойного союза (то) и определительное придаточное (который). Этому соответствует вариант B. В варианте A нарушена структура главной части, в варианте C неправильный порядок частей предложения.'''
    },

    {
        'id': 77,
        'image': r'/home/KrE3st/bot/Задания/Задания 6/6.2.png',  # схема: [  ], (что), (когда), (где)
        'start_text': "Я помню...",
        'sentences': [
            "A) что когда мы гуляли где находится парк было весело",
            "B) когда мы гуляли что где находится парк было весело",
            "C) что когда мы гуляли в парке где играли дети было весело"
        ],
        'correct': 'C',
        'type': 'type6',
        'keyboard': kb_type2,
        'explanation': '''По схеме требуется последовательное подчинение: изъяснительное придаточное (что), придаточное времени (когда) и придаточное места (где). Этому соответствует вариант C. В вариантах A и B нарушена логическая связь между частями предложения.'''
    },

    {
        'id': 78,
        'image': r'/home/KrE3st/bot/Задания/Задания 6/6.3.png',  # схема: (Хотя), [  ], (потому что)
        'start_text': "Хотя было уже поздно...",
        'sentences': [
            "A) потому что мы продолжали работать было интересно",
            "B) мы продолжали работать потому что было интересно",
            "C) мы потому что было интересно продолжали работать"
        ],
        'correct': 'B',
        'type': 'type6',
        'keyboard': kb_type2,
        'explanation': '''По схеме после уступительного придаточного (хотя) должна идти главная часть, а затем придаточное причины (потому что). Этому соответствует вариант B. В варианте A нарушен порядок частей, в варианте C неправильно размещено придаточное причины.'''
    },

    {
        'id': 79,
        'image': r'/home/KrE3st/bot/Задания/Задания 6/6.4.png',  # схема: [  ], (и когда), (что)
        'start_text': "Мы сидели у окна...",
        'sentences': [
            "A) и когда начался дождь что стало грустно",
            "B) и когда начался дождь мы увидели что на улице никого нет",
            "C) что когда начался дождь и стало грустно"
        ],
        'correct': 'B',
        'type': 'type6',
        'keyboard': kb_type2,
        'explanation': '''По схеме требуется: главная часть, союз "и" с придаточным времени (когда), затем придаточное изъяснительное (что). Этому соответствует вариант B. В вариантах A и C нарушена логическая связь между частями и их последовательность.'''
    },

    {
        'id': 80,
        'image': r'/home/KrE3st/bot/Задания/Задания 6/6.5.png',  # схема: [  ], (чтобы), (если)
        'start_text': "Я решил позвонить...",
        'sentences': [
            "A) если нужно чтобы договориться о встрече",
            "B) чтобы договориться о встрече если будет возможность",
            "C) чтобы если будет возможность договориться о встрече"
        ],
        'correct': 'B',
        'type': 'type6',
        'keyboard': kb_type2,
        'explanation': '''По схеме после главной части должно идти придаточное цели (чтобы), а затем условное придаточное (если). Этому соответствует вариант B. В варианте A неправильный порядок союзов, в варианте C придаточные неправильно соединены между собой.'''
    },
    {
        'id': 81,
        'image': r'/home/KrE3st/bot/Задания/Задания 6/6.6.png',  # схема: [  ], (где), и [  ], (который)
        'start_text': "Мы нашли поляну...",
        'sentences': [
            "A) где можно отдохнуть и поставили палатку которая была совсем новая",
            "B) которая была совсем новая и где можно отдохнуть поставили палатку",
            "C) и поставили палатку которая где можно отдохнуть была совсем новая"
        ],
        'correct': 'A',
        'type': 'type6',
        'keyboard': kb_type2,
        'explanation': '''По схеме требуется: главное предложение с придаточным места (где), соединительный союз "и", вторая часть главного предложения с определительным придаточным (который). Этому соответствует вариант A. В вариантах B и C нарушен порядок частей предложения и их связь.'''
    },

    {
        'id': 82,
        'image': r'/home/KrE3st/bot/Задания/Задания 6/6.7.png',  # схема: (По мере того как), [  ], (что)
        'start_text': "По мере того как поднималось солнце...",
        'sentences': [
            "A) что становилось теплее мы заметили",
            "B) мы заметили что становится теплее",
            "C) становилось теплее что мы заметили"
        ],
        'correct': 'B',
        'type': 'type6',
        'keyboard': kb_type2,
        'explanation': '''По схеме после придаточного времени с союзом "по мере того как" должна идти главная часть, а затем изъяснительное придаточное (что). Этому соответствует вариант B. В вариантах A и C нарушен порядок частей предложения.'''
    },

    {
        'id': 83,
        'image': r'/home/KrE3st/bot/Задания/Задания 6/6.8.png',  # схема: [  ], (что), (если), (то)
        'start_text': "Я думаю...",
        'sentences': [
            "A) что если пойдёт дождь то мы останемся дома",
            "B) если пойдёт дождь что то мы останемся дома",
            "C) что то мы останемся дома если пойдёт дождь"
        ],
        'correct': 'A',
        'type': 'type6',
        'keyboard': kb_type2,
        'explanation': '''По схеме требуется: главная часть, изъяснительное придаточное (что), условное придаточное с двойным союзом (если...то). Этому соответствует вариант A. В вариантах B и C нарушен порядок союзов и связь между частями предложения.'''
    },

    {
        'id': 84,
        'image': r'/home/KrE3st/bot/Задания/Задания 6/6.9.png',  # схема: [  ], (и когда), (хотя)
        'start_text': "Мы продолжали идти вперёд...",
        'sentences': [
            "A) и когда начался дождь хотя все устали",
            "B) хотя и когда начался дождь все устали",
            "C) и хотя все устали когда начался дождь"
        ],
        'correct': 'A',
        'type': 'type6',
        'keyboard': kb_type2,
        'explanation': '''По схеме требуется: главная часть, союз "и" с придаточным времени (когда), затем придаточное уступки (хотя). Этому соответствует вариант A. В вариантах B и C нарушен порядок союзов и придаточных частей.'''
    },

    {
        'id': 85,
        'image': r'/home/KrE3st/bot/Задания/Задания 6/6.10.png',  # схема: [  ], (чтобы), (который), (где)
        'start_text': "Мы приехали в город...",
        'sentences': [
            "A) чтобы посетить музей который находится где расположен центр",
            "B) чтобы посетить музей который находится в центре где проходят экскурсии",
            "C) где который находится чтобы посетить музей в центре"
        ],
        'correct': 'B',
        'type': 'type6',
        'keyboard': kb_type2,
        'explanation': '''По схеме требуется: главная часть, придаточное цели (чтобы), определительное придаточное (который) и придаточное места (где). Этому соответствует вариант B. В варианте A нарушена логика построения предложения, в варианте C неправильный порядок частей.'''
    },
    {
        'id': 86,
        'image': r'/home/KrE3st/bot/Задания/Задания 6/6.11.png',  # схема: [  ], (так что), (хотя)
        'start_text': "Дождь лил весь день...",
        'sentences': [
            "A) так что все промокли хотя были под зонтами",
            "B) хотя были под зонтами так что все промокли",
            "C) так что хотя были под зонтами все промокли"
        ],
        'correct': 'A',
        'type': 'type6',
        'keyboard': kb_type2,
        'explanation': '''По схеме требуется: главная часть, придаточное следствия (так что) и придаточное уступки (хотя). Этому соответствует вариант A. В вариантах B и C нарушен порядок придаточных частей, что искажает логику высказывания.'''
    },

    {
        'id': 87,
        'image': r'/home/KrE3st/bot/Задания/Задания 6/6.12.png',  # схема: (В то время как), [  ], (который)
        'start_text': "В то время как шёл урок...",
        'sentences': [
            "A) который был контрольным в коридоре стоял шум",
            "B) в коридоре стоял шум который мешал заниматься",
            "C) в коридоре который был шумным стоял шум"
        ],
        'correct': 'B',
        'type': 'type6',
        'keyboard': kb_type2,
        'explanation': '''По схеме после придаточного времени с союзом "в то время как" должна идти главная часть, а затем определительное придаточное (который). Этому соответствует вариант B. В варианте A нарушена логика связи частей, в варианте C неправильно построено определительное придаточное.'''
    },

    {
        'id': 88,
        'image': r'/home/KrE3st/bot/Задания/Задания 6/6.13.png',  # схема: [  ], (что), (будто)
        'start_text': "Мне показалось...",
        'sentences': [
            "A) что в доме будто кто-то ходит",
            "B) будто в доме что кто-то ходит",
            "C) что кто-то ходит будто в доме"
        ],
        'correct': 'A',
        'type': 'type6',
        'keyboard': kb_type2,
        'explanation': '''По схеме требуется: главная часть, изъяснительное придаточное (что) и придаточное сравнительное (будто). Этому соответствует вариант A. В вариантах B и C нарушен порядок союзов и связь между частями предложения.'''
    },

    {
        'id': 89,
        'image': r'/home/KrE3st/bot/Задания/Задания 6/6.14.png',  # схема: [  ], (и), (потому что), (когда)
        'start_text': "Мы решили вернуться домой...",
        'sentences': [
            "A) и потому что темнело когда начался дождь",
            "B) и закончить работу потому что темнело когда начался дождь",
            "C) когда начался дождь и потому что темнело"
        ],
        'correct': 'B',
        'type': 'type6',
        'keyboard': kb_type2,
        'explanation': '''По схеме требуется: главная часть, соединительный союз "и", затем придаточное причины (потому что) и придаточное времени (когда). Этому соответствует вариант B. В вариантах A и C нарушена последовательность частей и их логическая связь.'''
    },

    {
        'id': 90,
        'image': r'/home/KrE3st/bot/Задания/Задания 6/6.15.png',  # схема: [  ], (чтобы), (если), (где)
        'start_text': "Мы вышли пораньше...",
        'sentences': [
            "A) чтобы успеть в музей если будет очередь где проходит выставка",
            "B) где проходит выставка чтобы успеть если будет очередь",
            "C) если будет очередь чтобы успеть где проходит выставка"
        ],
        'correct': 'A',
        'type': 'type6',
        'keyboard': kb_type2,
        'explanation': '''По схеме требуется: главная часть, придаточное цели (чтобы), условное придаточное (если) и придаточное места (где). Этому соответствует вариант A. В вариантах B и C нарушен порядок придаточных частей, что делает предложение нелогичным.'''
    }

]


def validate_task(task):
    try:
        base_required_fields = ['id', 'type', 'correct', 'explanation']
        for field in base_required_fields:
            if field not in task:
                return False, f"Missing required field: {field}"

        if not isinstance(task['id'], int) or task['id'] < 1:
            return False, "Invalid task ID: must be positive integer"

        valid_types = ['type1', 'type2', 'type3', 'type4', 'type5', 'type6']
        if task['type'] not in valid_types:
            return False, f"Invalid task type: {task['type']}"

        keyboard_mapping = {
            'type1': kb_type1,
            'type2': kb_type2,
            'type3': kb_type3,
            'type4': None,
            'type5': kb_type2,
            'type6': kb_type2
        }

        valid_answers = {
            'type1': ['A', 'B', 'C', 'D'],
            'type2': ['A', 'B', 'C'],
            'type3': ['true', 'false'],
            'type4': None,
            'type5': ['A', 'B', 'C'],
            'type6': ['A', 'B', 'C']
        }

        if task['type'] in ['type1', 'type2', 'type3', 'type5', 'type6']:
            if 'keyboard' not in task:
                return False, f"Missing keyboard for {task['type']}"

            if task['keyboard'] != keyboard_mapping[task['type']]:
                return False, f"Invalid keyboard for {task['type']}"

            if valid_answers[task['type']] and task['correct'] not in valid_answers[task['type']]:
                return False, f"Invalid answer format for {task['type']}: {task['correct']}"

        if task['type'] != 'type4':
            if 'image' not in task:
                return False, "Missing image field"
            if not isinstance(task['image'], str):
                return False, "Image path must be string"
            if not task['image'].endswith(('.png', '.jpg', '.jpeg')):
                return False, "Invalid image format"

        if task['type'] == 'type4':
            if 'instruction' not in task:
                return False, "Missing instruction for type4"
            if not isinstance(task['instruction'], str):
                return False, "Instruction must be string"

        if task['type'] == 'type5':
            if 'sentences' not in task:
                return False, "Missing sentences for type5"
            if len(task['sentences']) != 3:
                return False, "Type5 requires exactly 3 sentences"
            if not all(s.startswith(('A)', 'B)', 'C)')) for s in task['sentences']):
                return False, "Invalid sentence format in type5"

        if task['type'] == 'type6':
            if 'start_text' not in task:
                return False, "Missing start_text for type6"
            if 'sentences' not in task:
                return False, "Missing sentences for type6"
            if len(task['sentences']) != 3:
                return False, "Type6 requires exactly 3 variants"
            if not all(s.startswith(('A)', 'B)', 'C)')) for s in task['sentences']):
                return False, "Invalid sentence format in type6"

        if not task['explanation'] or not isinstance(task['explanation'], str):
            return False, "Invalid or empty explanation"
        if len(task['explanation'].strip()) < 10:
            return False, "Explanation is too short"

        return True, "Task is valid"

    except Exception as e:
        return False, f"Validation error: {str(e)}"


# Проверка всей базы данных
def validate_database():
    for task in BD:
        is_valid, message = validate_task(task)
        if not is_valid:
            logging.error(f"Task {task['id']}: {message}")
            return False
    return True


@dp.message()
async def handle_message(message: types.Message):
    user_id = message.from_user.id

    # Проверяем режим тренировки
    if user_id in user_training_state and user_training_state[user_id]['is_training']:
        if user_id in user_training_data:
            current_task = user_training_data[user_id]

            # Очищаем ответ пользователя и правильный ответ от точки в конце
            user_answer = message.text.strip().rstrip('.')
            correct_answer = current_task['correct'].strip().rstrip('.')

            if user_answer.lower() == correct_answer.lower():
                await message.answer(
                    "✅ Верно!\n\n"
                    "Выберите действие:",
                    reply_markup=training_kb
                )
            else:
                await message.answer(
                    "❌ Неверно.\n\n"
                    f"Правильный вариант:\n{current_task['correct']}\n\n"
                    f"Пояснение:\n{current_task['explanation']}\n\n"
                    "Выберите действие:",
                    reply_markup=training_kb
                )
        return

    # Проверяем обычные задания
    if user_id in user_tasks:
        user = user_tasks[user_id]
        if user['current'] >= len(user['tasks']):
            return

        current_task = user['tasks'][user['current']]
        if current_task['type'] == 'type4':
            user_answer = ''.join(char for char in message.text if char.isdigit())
            correct_answer = ''.join(char for char in current_task['correct'] if char.isdigit())

            # Добавляем подробное логирование
            logging.info(f"""
            Task ID: {current_task['id']}
            Original user answer: {message.text}
            Cleaned user answer: {user_answer}
            Correct answer: {correct_answer}
            """)

            is_correct = user_answer == correct_answer

            if is_correct:
                user['correct'] += 1
                sticker_category = 'perfect' if user['correct'] > 2 else 'good'
                await message.answer_sticker(random.choice(STICKERS[sticker_category]))
                await message.answer(random.choice(MESSAGES[sticker_category]))
            else:
                await message.answer_sticker(random.choice(STICKERS['wrong']))
                await message.answer(
                    f"{random.choice(MESSAGES['wrong'])}\n\n"
                    f"📝 Пояснение:\n{current_task['explanation']}\n\n"
                    f"✨ Правильный ответ: {current_task['correct']}"
                )

            user['current'] += 1
            if user['current'] < len(user['tasks']):
                await asyncio.sleep(2)
                await send_task(user_id, user['tasks'][user['current']])
            else:
                await show_results(user_id, message)


@dp.callback_query(lambda c: c.data == "back_to_admin")
async def back_to_admin_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "👨‍💻 Панель администратора\n\n"
        "Выберите действие:",
        reply_markup=admin_kb
    )


def save_all_data():
    try:
        all_data = {
            'users': {
                str(user_id): {
                    'username': user_info['username'],
                    'tasks_completed': int(user_info['tasks_completed']),
                    'reg_date': user_info['reg_date'],
                    'last_active': user_info['last_active'],
                    'achievements': list(user_info.get('achievements', set())),
                    'perfect_scores': int(user_info.get('perfect_scores', 0))
                }
                for user_id, user_info in users.items()
            },
            'user_streaks': {
                str(user_id): int(streak)
                for user_id, streak in user_streaks.items()
            },
            'user_completed_tasks': {
                str(user_id): list(tasks)
                for user_id, tasks in user_completed_tasks.items()
            },
            'user_last_tasks': {
                str(user_id): time
                for user_id, time in user_last_tasks.items()
            },
            'last_save': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        logging.info("All data saved successfully")

    except Exception as e:
        logging.error(f"Error saving data: {e}")


def check_paths():
    try:
        required_dirs = [BASE_DIR, IMAGES_DIR]
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                logging.info(f"Created directory: {dir_path}")
    except Exception as e:
        logging.error(f"Error checking paths: {e}")


async def rate_limit(user_id: int, action: str, limit: int = 5, period: int = 60):
    try:
        key = f"{user_id}:{action}"
        current_time = time.time()

        if key not in rate_limits:
            rate_limits[key] = {"count": 1, "first_request": current_time}
            return True

        if current_time - rate_limits[key]["first_request"] > period:
            rate_limits[key] = {"count": 1, "first_request": current_time}
            return True

        rate_limits[key]["count"] += 1
        return rate_limits[key]["count"] <= limit
    except Exception as e:
        logging.error(f"Error in rate limit: {e}")
        return True


async def error_handler(update: types.Update, exception: Exception):
    try:
        user_id = update.message.from_user.id if update.message else None
        error_msg = f"Error: {exception}\nUpdate: {update}"
        logging.error(error_msg)

        if user_id:
            await update.message.answer(
                "Произошла ошибка. Используйте /start для перезапуска."
            )

            # Очистка данных пользователя при ошибке
            if user_id in user_tasks:
                del user_tasks[user_id]
            if user_id in user_training_state:
                del user_training_state[user_id]
            if user_id in user_training_data:
                del user_training_data[user_id]

    except Exception as e:
        logging.error(f"Error in error handler: {e}")


@dp.callback_query(lambda c: c.data.startswith("admin_"))
async def process_admin_callback(callback: CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("У вас нет прав администратора", show_alert=True)
        return

    action = callback.data.split("_")[1]

    if action == "stats":
        # Статистика бота
        total_users = len(users)
        active_today = sum(1 for user in users.values()
                           if user['last_active'] == datetime.now().strftime("%d.%m.%Y"))
        total_tasks_completed = sum(user['tasks_completed'] for user in users.values())

        stats_text = (
            "📊 *Статистика бота:*\n\n"
            f"👥 Всего пользователей: {total_users}\n"
            f"📱 Активных сегодня: {active_today}\n"
            f"✅ Всего решено заданий: {total_tasks_completed}\n"
            f"⚠️ Заблокировано: {len(banned_users)}\n"
            f"🕒 Данные на: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        )

        await callback.message.edit_text(
            stats_text,
            reply_markup=admin_kb,
            parse_mode=ParseMode.MARKDOWN
        )
    elif action == "logs":
        try:
            # Читаем последние 20 строк лога
            with open('bot.log', 'r') as f:
                logs = f.readlines()[-20:]

            logs_text = "📋 *Последние логи:*\n\n"
            for log in logs:
                log = log.strip()
                if "ERROR" in log:
                    logs_text += f"❌ `{log}`\n"
                elif "WARNING" in log:
                    logs_text += f"⚠️ `{log}`\n"
                else:
                    logs_text += f"ℹ️ `{log}`\n"
                logs_text += "───────────────\n"

            logs_kb = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text="🔄 Обновить", callback_data="admin_logs"),
                    InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_admin")
                ]
            ])

            await callback.message.edit_text(
                logs_text,
                reply_markup=logs_kb,
                parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            await callback.message.edit_text(
                f"❌ Ошибка при чтении логов: {str(e)}",
                reply_markup=admin_kb
            )


async def send_notification(user_id: int):
    try:
        message = "🎯 Доступны новые задания! Заходите порешать."
        await bot.send_message(user_id, message)
    except Exception as e:
        logging.error(f"Error sending notification to user {user_id}: {e}")


async def notification_manager():
    while True:
        try:
            current_time = datetime.now()

            for user_id in subscribed_users:
                if user_id in user_next_notification:
                    notification_time = user_next_notification[user_id]

                    if current_time >= notification_time:
                        await send_notification(user_id)
                        del user_next_notification[user_id]

                elif current_time.hour == 0 and current_time.minute < 5:
                    await send_notification(user_id)

            await asyncio.sleep(60)

        except Exception as e:
            logging.error(f"Error in notification manager: {e}")
            await asyncio.sleep(60)


async def main():
    try:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            filename='bot.log'
        )

        # Загружаем сохраненные данные при запуске
        load_rating_data()

        # Регистрация роутера
        dp.include_router(router)

        # Запускаем задачи
        asyncio.create_task(reset_daily_limits())
        asyncio.create_task(notification_manager())  # Добавляем эту строку
        asyncio.create_task(auto_save())

        # Запуск бота
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logging.error(f"Critical error: {e}")
        save_rating_data()
        raise


if __name__ == "__main__":
    asyncio.run(main())

