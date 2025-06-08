import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config.config import BOT_TOKEN, LOG_FILE, LOG_FORMAT, ADMINS
from storage.storage import user_storage
from services.weather_api import WeatherAPI

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация основных компонентов бота
bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# Локализация текстовых сообщений
TEXTS = {
    'ru': {
        'welcome': "Привет, {name}! Выберите язык:",
        'language_set': "Язык установлен: Русский",
        'current_city': "Твой текущий город: <b>{city}</b>",
        'weather_buttons': "Используй кнопки ниже для работы с ботом.",
        'ask_city': "Я бот погоды. Для начала скажи, в каком городе ты живешь?\n\nПожалуйста, введите название города:",
        'weather_request': "⏳ Запрашиваю данные о погоде...",
        'forecast_request': "⏳ Запрашиваю прогноз погоды...",
        'no_city': "Сначала укажите город, нажав кнопку 'Сменить город 🏙️'",
        'weather_error': "Не удалось получить данные о погоде. Попробуйте позже.",
        'forecast_error': "Не удалось получить прогноз погоды. Попробуйте позже.",
        'change_city_prompt': "Введите название вашего города:",
        'city_check': "⏳ Проверяю город...",
        'city_invalid': "Не удалось найти такой город. Попробуйте еще раз.",
        'city_saved': "Город <b>{city}</b> сохранен!\nТеперь вы можете узнать погоду.",
        'help_text': (
            "📝 <b>Доступные команды:</b>\n\n"
            "🌤️ <b>Узнать погоду</b> - текущая погода в вашем городе\n"
            "📅 <b>Прогноз на 4 дня</b> - прогноз погоды на ближайшие дни\n"
            "🏙️ <b>Сменить город</b> - изменить город для прогноза погоды\n"
            "🌐 <b>Сменить язык</b> - изменить язык интерфейса\n"
            "❓ <b>Помощь</b> - показать это сообщение\n\n"
            "Вы также можете использовать команды:\n"
            "/weather, /forecast, /change_city, /change_language, /help\n"
        ),
        'admin_help': (
            "\n<b>Админские команды:</b>\n\n"
            "/stats - статистика бота\n"
            "/ban (user_id) - заблокировать пользователя\n"
            "/unban (user_id) - разблокировать пользователя\n"
            "/broadcast (сообщение) - рассылка всем пользователям\n"
        ),
        'buttons': {
            'weather': "Узнать погоду 🌤️",
            'forecast': "Прогноз на 4 дня 📅",
            'change_city': "Сменить город 🏙️",
            'change_language': "Сменить язык 🌐",
            'help': "Помощь ❓"
        }
    },
    'en': {
        'welcome': "Hello, {name}! Choose your language:",
        'language_set': "Language set to: English",
        'current_city': "Your current city: <b>{city}</b>",
        'weather_buttons': "Use the buttons below to interact with the bot.",
        'ask_city': "I'm a weather bot. First, tell me what city you live in?\n\nPlease enter your city name:",
        'weather_request': "⏳ Requesting weather data...",
        'forecast_request': "⏳ Requesting weather forecast...",
        'no_city': "Please set your city first by clicking 'Change city 🏙️'",
        'weather_error': "Failed to get weather data. Please try again later.",
        'forecast_error': "Failed to get weather forecast. Please try again later.",
        'change_city_prompt': "Enter your city name:",
        'city_check': "⏳ Checking city...",
        'city_invalid': "Couldn't find this city. Please try again.",
        'city_saved': "City <b>{city}</b> saved!\nNow you can check the weather.",
        'help_text': (
            "📝 <b>Available commands:</b>\n\n"
            "🌤️ <b>Get weather</b> - current weather in your city\n"
            "📅 <b>4-day forecast</b> - weather forecast for upcoming days\n"
            "🏙️ <b>Change city</b> - change city for weather forecast\n"
            "🌐 <b>Change language</b> - change interface language\n"
            "❓ <b>Help</b> - show this message\n\n"
            "You can also use commands:\n"
            "/weather, /forecast, /change_city, /change_language, /help"
        ),
        'admin_help': (
            "\n\n<b>Admin commands:</b>\n"
            "/stats - bot statistics\n"
            "/ban (user_id) - ban user\n"
            "/unban (user_id) - unban user\n"
            "/broadcast (message) - send message to all users"
        ),
        'buttons': {
            'weather': "Get weather 🌤️",
            'forecast': "4-day forecast 📅",
            'change_city': "Change city 🏙️",
            'change_language': "Change language 🌐",
            'help': "Help ❓"
        }
    }
}

# Состояния FSM
class WeatherStates(StatesGroup):
    """Состояния конечного автомата для бота."""
    waiting_for_city = State()
    waiting_for_language = State()


# Создание клавиатуры
def get_main_keyboard(lang: str = 'ru'):
    texts = TEXTS[lang]['buttons']
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=texts['weather']), KeyboardButton(text=texts['forecast'])],
            [KeyboardButton(text=texts['change_city']), KeyboardButton(text=texts['change_language'])],
            [KeyboardButton(text=texts['help'])]
        ],
        resize_keyboard=True
    )


def get_language_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Русский", callback_data="lang_ru"),
             InlineKeyboardButton(text="English", callback_data="lang_en")]
        ]
    )


# Middleware для проверки бана
@dp.message.middleware()
async def check_ban_middleware(handler, event, data):
    user_id = event.from_user.id
    if user_storage.is_banned(user_id):
        lang = user_storage.get_user_language(user_id)
        await event.answer(
            "🚫 Вы заблокированы и не можете использовать бота" if lang == 'ru' else "🚫 You are banned and cannot use the bot")
        return
    return await handler(event, data)


# Команда /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(
        TEXTS['ru']['welcome'].format(name=message.from_user.first_name),
        reply_markup=get_language_keyboard()
    )
    await state.set_state(WeatherStates.waiting_for_language)



# Обработка выбора языка
@dp.callback_query(F.data.startswith("lang_"))
async def set_language(callback: types.CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    user_id = callback.from_user.id
    user_storage.set_user_language(user_id, lang)

    await callback.message.edit_text(
        TEXTS[lang]['language_set']
    )

    city = user_storage.get_user_city(user_id)
    if city:
        await callback.message.answer(
            f"{TEXTS[lang]['current_city'].format(city=city)}\n"
            f"{TEXTS[lang]['weather_buttons']}",
            reply_markup=get_main_keyboard(lang)
        )
    else:
        await callback.message.answer(
            TEXTS[lang]['ask_city'],
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(WeatherStates.waiting_for_city)
    await callback.answer()


# Команда смены языка
@dp.message(F.text.in_(
    [TEXTS['ru']['buttons']['change_language'], TEXTS['en']['buttons']['change_language'], "/change_language"]))
async def change_language(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    current_lang = user_storage.get_user_language(user_id)

    await message.answer(
        TEXTS[current_lang]['welcome'].format(name=message.from_user.first_name),
        reply_markup=get_language_keyboard()
    )
    await state.set_state(WeatherStates.waiting_for_language)


# Обработка текстовых сообщений (кнопок)
@dp.message(F.text.in_([TEXTS['ru']['buttons']['weather'], TEXTS['en']['buttons']['weather'], "/weather"]))
async def get_weather(message: types.Message):
    user_id = message.from_user.id
    city = user_storage.get_user_city(user_id)
    lang = user_storage.get_user_language(user_id)

    if not city:
        await message.answer(TEXTS[lang]['no_city'])
        return

    user_storage.increment_stat('weather_requests')
    await message.answer(TEXTS[lang]['weather_request'])

    weather_data = WeatherAPI.get_weather(city, lang)
    if weather_data:
        await message.answer(WeatherAPI.format_weather(weather_data, lang))
    else:
        await message.answer(TEXTS[lang]['weather_error'])


@dp.message(F.text.in_([TEXTS['ru']['buttons']['forecast'], TEXTS['en']['buttons']['forecast'], "/forecast"]))
async def get_forecast(message: types.Message):
    user_id = message.from_user.id
    city = user_storage.get_user_city(user_id)
    lang = user_storage.get_user_language(user_id)

    if not city:
        await message.answer(TEXTS[lang]['no_city'])
        return

    user_storage.increment_stat('forecast_requests')
    await message.answer(TEXTS[lang]['forecast_request'])

    forecast_data = WeatherAPI.get_forecast(city, lang)
    if forecast_data:
        await message.answer(WeatherAPI.format_forecast(forecast_data, lang))
    else:
        await message.answer(TEXTS[lang]['forecast_error'])


@dp.message(F.text.in_([TEXTS['ru']['buttons']['change_city'], TEXTS['en']['buttons']['change_city'], "/change_city"]))
async def change_city(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = user_storage.get_user_language(user_id)

    await message.answer(
        TEXTS[lang]['change_city_prompt'],
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(WeatherStates.waiting_for_city)


@dp.message(F.text.in_([TEXTS['ru']['buttons']['help'], TEXTS['en']['buttons']['help'], "/help"]))
async def show_help(message: types.Message):
    user_id = message.from_user.id
    lang = user_storage.get_user_language(user_id)

    help_text = TEXTS[lang]['help_text']
    if user_id in ADMINS:
        help_text += TEXTS[lang]['admin_help']

    await message.answer(
        help_text,
        reply_markup=get_main_keyboard(lang)
    )

# Обработка ввода города
@dp.message(WeatherStates.waiting_for_city)
async def process_city(message: types.Message, state: FSMContext):
    city = message.text.strip()
    user_id = message.from_user.id
    lang = user_storage.get_user_language(user_id)

    if len(city) < 2:
        await message.answer(TEXTS[lang]['city_invalid'])
        return

    await message.answer(TEXTS[lang]['city_check'])

    weather_data = WeatherAPI.get_weather(city, lang)
    if not weather_data or 'cod' not in weather_data or weather_data['cod'] != 200:
        await message.answer(TEXTS[lang]['city_invalid'])
        return

    user_storage.set_user_city(user_id, city)
    await state.clear()
    await message.answer(
        TEXTS[lang]['city_saved'].format(city=city),
        reply_markup=get_main_keyboard(lang)
    )


# Админ-команды
@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    if message.from_user.id not in ADMINS:
        return

    stats = user_storage.get_stats()
    await message.answer(
        f"📊 Статистика бота:\n\n"
        f"👥 Всего пользователей: {stats['total_users']}\n"
        f"🟢 Активных пользователей: {stats['active_users']}\n"
        f"🌤️ Запросов погоды: {stats['weather_requests']}\n"
        f"📅 Запросов прогноза: {stats['forecast_requests']}"
    )


@dp.message(Command("ban"))
async def cmd_ban(message: types.Message):
    if message.from_user.id not in ADMINS:
        return

    try:
        user_id = int(message.text.split()[1])
        user_storage.ban_user(user_id)
        await message.answer(f"✅ Пользователь {user_id} заблокирован")
    except (IndexError, ValueError):
        await message.answer("Использование: /ban <user_id>")


@dp.message(Command("unban"))
async def cmd_unban(message: types.Message):
    if message.from_user.id not in ADMINS:
        return

    try:
        user_id = int(message.text.split()[1])
        user_storage.unban_user(user_id)
        await message.answer(f"✅ Пользователь {user_id} разблокирован")
    except (IndexError, ValueError):
        await message.answer("Использование: /unban <user_id>")


@dp.message(Command("broadcast"))
async def cmd_broadcast(message: types.Message):
    if message.from_user.id not in ADMINS:
        return

    if len(message.text.split()) < 2:
        await message.answer("Использование: /broadcast <сообщение>")
        return


    broadcast_text = ' '.join(message.text.split()[1:])
    users = user_storage.data.keys()
    success = 0
    failed = 0

    await message.answer(f"⏳ Рассылка начата для {len(users)} пользователей...")

    for user_id in users:
        try:
            await bot.send_message(user_id, broadcast_text)
            success += 1
        except Exception as e:
            logger.error(f"Ошибка при рассылке для {user_id}: {e}")
            failed += 1
        await asyncio.sleep(0.1)

    await message.answer(
        f"✅ Рассылка завершена:\n"
        f"Успешно: {success}\n"
        f"Не удалось: {failed}"
    )


# Запуск бота
async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    """Основная функция запуска бота."""
    try:
        print("Бот запущен")
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\nБот остановлен.")
