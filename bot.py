from datetime import datetime
import logging
import os
import threading

from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from dotenv import load_dotenv
from flask import Flask
import requests


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

# Получаем токены
TG_KEY = os.getenv("TG_KEY")
API_KEY = os.getenv("API_KEY")
PORT = int(os.getenv("PORT", 10000))

if not TG_KEY:
    raise ValueError("Не найден TG_KEY в переменных окружения")
if not API_KEY:
    raise ValueError("Не найден API_KEY в переменных окружения")

# Инициализация бота и диспетчера
bot = Bot(token=TG_KEY, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# Инициализация Flask приложения
app = Flask(__name__)

# Город по умолчанию
DEFAULT_CITY = "Saint Petersburg"


def get_weather(city: str) -> str:
    """
    Получает данные о погоде для указанного города
    """
    try:
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric",
            "lang": "ru",
        }

        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather", params=params
        )
        response.raise_for_status()
        data = response.json()

        # Форматируем данные о погоде
        weather_info = f"🌤 <b>Погода в {city}</b>\n\n"
        weather_info += (
            f"• <b>Состояние:</b> {data['weather'][0]['description'].capitalize()}\n"
        )
        weather_info += f"• <b>Температура:</b> {data['main']['temp']} °C\n"
        weather_info += f"• <b>Ощущается как:</b> {data['main']['feels_like']} °C\n"
        weather_info += f"• <b>Влажность:</b> {data['main']['humidity']}%\n"
        weather_info += f"• <b>Давление:</b> {data['main']['pressure']} гПа\n"

        if "grnd_level" in data["main"]:
            weather_info += (
                f"• <b>Давление у земли:</b> {data['main']['grnd_level']} гПа\n"
            )

        weather_info += f"• <b>Скорость ветра:</b> {data['wind']['speed']} м/с\n"

        # Время заката
        sunset_timestamp = data["sys"]["sunset"]
        sunset_time = datetime.fromtimestamp(sunset_timestamp).strftime("%H:%M:%S")
        weather_info += f"• <b>Закат:</b> {sunset_time}\n"

        return weather_info

    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            return f"❌ Город '{city}' не найден. Проверьте правильность написания."
        else:
            return f"❌ Ошибка при получении данных: {e}"
    except requests.exceptions.RequestException as e:
        return f"❌ Ошибка соединения: {e}"
    except KeyError as e:
        return f"❌ Ошибка в данных от API: отсутствует ключ {e}"
    except Exception as e:
        return f"❌ Неизвестная ошибка: {e}"


# Создаем клавиатуру
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌤 Погода в СПб"), KeyboardButton(text="❓ Помощь")],
            [KeyboardButton(text="🏙 Сменить город")],
        ],
        resize_keyboard=True,
    )
    return keyboard


# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    welcome_text = (
        "👋 <b>Добро пожаловать в Weather Bot!</b>\n\n"
        "Я могу показать актуальную погоду в любом городе мира.\n\n"
        "<b>Доступные команды:</b>\n"
        "• /start - начать работу\n"
        "• /help - помощь\n"
        "• /weather <город> - погода в указанном городе\n"
        "• /city <город> - установить город по умолчанию\n\n"
        "<b>Быстрые кнопки:</b>\n"
        "• Погода в СПб - текущая погода\n"
        "• Сменить город - установить другой город"
    )

    await message.answer(welcome_text, reply_markup=get_main_keyboard())

    # Показываем погоду в городе по умолчанию
    weather_info = get_weather(DEFAULT_CITY)
    await message.answer(weather_info)


# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "📖 <b>Помощь по использованию бота</b>\n\n"
        "<b>Команды:</b>\n"
        "• /start - начать работу с ботом\n"
        "• /help - показать эту справку\n"
        "• /weather <город> - погода в указанном городе\n"
        "• /city <город> - установить город по умолчанию\n\n"
        "<b>Примеры:</b>\n"
        "<code>/weather Moscow</code> - погода в Москве\n"
        "<code>/city London</code> - установить Лондон городом по умолчанию\n\n"
        "<b>Быстрые кнопки</b> ниже позволяют быстро получить погоду без ввода команд."
    )
    await message.answer(help_text)


# Обработчик команды /weather
@dp.message(Command("weather"))
async def cmd_weather(message: types.Message):
    # Получаем город из команды (всё после /weather)
    command_parts = message.text.split()

    if len(command_parts) < 2:
        await message.answer(
            "❌ Укажите город после команды.\n"
            "<b>Пример:</b> <code>/weather Moscow</code>"
        )
        return

    city = " ".join(command_parts[1:])
    await message.answer(f"🔍 Запрашиваю погоду для {city}...")

    weather_info = get_weather(city)
    await message.answer(weather_info)


# Обработчик команды /city
@dp.message(Command("city"))
async def cmd_city(message: types.Message):
    command_parts = message.text.split()

    if len(command_parts) < 2:
        await message.answer(
            "❌ Укажите город после команды.\n"
            "<b>Пример:</b> <code>/city London</code>"
        )
        return

    city = " ".join(command_parts[1:])

    # Проверяем, что город существует, запрашивая погоду
    weather_info = get_weather(city)

    if weather_info.startswith("❌"):
        await message.answer(weather_info)
    else:
        global DEFAULT_CITY
        DEFAULT_CITY = city
        await message.answer(
            f"✅ Город по умолчанию изменен на: <b>{city}</b>\n\n{weather_info}"
        )


# Обработчик кнопки "Погода в СПб"
@dp.message(F.text == "🌤 Погода в СПб")
async def weather_spb(message: types.Message):
    await message.answer("🔍 Запрашиваю погоду в Санкт-Петербурге...")
    weather_info = get_weather("Saint Petersburg")
    await message.answer(weather_info)


# Обработчик кнопки "Помощь"
@dp.message(F.text == "❓ Помощь")
async def help_button(message: types.Message):
    await cmd_help(message)


# Обработчик кнопки "Сменить город"
@dp.message(F.text == "🏙 Сменить город")
async def change_city_button(message: types.Message):
    await message.answer(
        "🏙 Чтобы установить город по умолчанию, используйте команду:\n"
        "<code>/city &lt;название города&gt;</code>\n\n"
        "<b>Пример:</b> <code>/city London</code>\n\n"
        "Или просто отправьте название города, и я покажу погоду в нем."
    )


# Обработчик текстовых сообщений (для произвольных городов)
@dp.message(F.text)
async def handle_city_input(message: types.Message):
    text = message.text.strip()

    # Игнорируем команды и кнопки, которые уже обработаны
    if text in ["🌤 Погода в СПб", "❓ Помощь", "🏙 Сменить город"]:
        return

    # Если текст не похож на команду, считаем его названием города
    if not text.startswith("/"):
        await message.answer(f"🔍 Запрашиваю погоду для {text}...")
        weather_info = get_weather(text)
        await message.answer(weather_info)


# Flask маршруты для здоровья приложения
@app.route("/")
def home():
    return {
        "status": "Bot is running",
        "bot": "@sppersonbot",
        "service": "Weather Telegram Bot",
    }


@app.route("/health")
def health():
    return {"status": "healthy"}


@app.route("/webhook", methods=["POST"])
def webhook():
    # Если потребуется вебхук в будущем
    return {"status": "ok"}


# Функция для запуска бота в отдельном потоке
def run_bot():
    import asyncio

    asyncio.run(start_bot())


async def start_bot():
    logger.info("Бот запускается...")
    await dp.start_polling(bot)


# Запуск приложения
if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    # Запускаем Flask приложение
    logger.info(f"Запуск Flask приложения на порту {PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
