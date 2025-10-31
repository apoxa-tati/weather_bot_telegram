from datetime import datetime
import logging
import os

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from dotenv import load_dotenv
import requests


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

# Получаем токены
TG_KEY = os.getenv("TG_KEY")
API_KEY = os.getenv("API_KEY")

if not TG_KEY:
    raise ValueError("Не найден TG_KEY в переменных окружения")
if not API_KEY:
    raise ValueError("Не найден API_KEY в переменных окружения")

# Инициализация бота и диспетчера
bot = Bot(token=TG_KEY)
dp = Dispatcher()

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
        weather_info = f"🌤 **Погода в {city}**\n\n"
        weather_info += (
            f"• **Состояние:** {data['weather'][0]['description'].capitalize()}\n"
        )
        weather_info += f"• **Температура:** {data['main']['temp']} °C\n"
        weather_info += f"• **Ощущается как:** {data['main']['feels_like']} °C\n"
        weather_info += f"• **Влажность:** {data['main']['humidity']}%\n"
        weather_info += f"• **Давление:** {data['main']['pressure']} гПа\n"

        if "grnd_level" in data["main"]:
            weather_info += (
                f"• **Давление у земли:** {data['main']['grnd_level']} гПа\n"
            )

        weather_info += f"• **Скорость ветра:** {data['wind']['speed']} м/с\n"

        # Время заката
        sunset_timestamp = data["sys"]["sunset"]
        sunset_time = datetime.fromtimestamp(sunset_timestamp).strftime("%H:%M:%S")
        weather_info += f"• **Закат:** {sunset_time}\n"

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
        "👋 **Добро пожаловать в Weather Bot!**\n\n"
        "Я могу показать актуальную погоду в любом городе мира.\n\n"
        "**Доступные команды:**\n"
        "• /start - начать работу\n"
        "• /help - помощь\n"
        "• /weather <город> - погода в указанном городе\n"
        "• /city <город> - установить город по умолчанию\n\n"
        "**Быстрые кнопки:**\n"
        "• Погода в СПб - текущая погода\n"
        "• Сменить город - установить другой город"
    )

    await message.answer(welcome_text, reply_markup=get_main_keyboard())

    # Показываем погоду в городе по умолчанию
    weather_info = get_weather(DEFAULT_CITY)
    await message.answer(weather_info, parse_mode="Markdown")


# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    help_text = (
        "📖 **Помощь по использованию бота**\n\n"
        "**Команды:**\n"
        "• /start - начать работу с ботом\n"
        "• /help - показать эту справку\n"
        "• /weather <город> - погода в указанном городе\n"
        "• /city <город> - установить город по умолчанию\n\n"
        "**Примеры:**\n"
        "`/weather Moscow` - погода в Москве\n"
        "`/city London` - установить Лондон городом по умолчанию\n\n"
        "**Быстрые кнопки** ниже позволяют быстро получить погоду без ввода команд."
    )
    await message.answer(help_text, parse_mode="Markdown")


# Обработчик команды /weather
@dp.message(Command("weather"))
async def cmd_weather(message: types.Message):
    # Получаем город из команды (всё после /weather)
    command_parts = message.text.split()

    if len(command_parts) < 2:
        await message.answer(
            "❌ Укажите город после команды.\n" "**Пример:** `/weather Moscow`",
            parse_mode="Markdown",
        )
        return

    city = " ".join(command_parts[1:])
    await message.answer(f"🔍 Запрашиваю погоду для {city}...")

    weather_info = get_weather(city)
    await message.answer(weather_info, parse_mode="Markdown")


# Обработчик команды /city
@dp.message(Command("city"))
async def cmd_city(message: types.Message):
    command_parts = message.text.split()

    if len(command_parts) < 2:
        await message.answer(
            "❌ Укажите город после команды.\n" "**Пример:** `/city London`",
            parse_mode="Markdown",
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
            f"✅ Город по умолчанию изменен на: **{city}**\n\n" f"{weather_info}",
            parse_mode="Markdown",
        )


# Обработчик кнопки "Погода в СПб"
@dp.message(F.text == "🌤 Погода в СПб")
async def weather_spb(message: types.Message):
    await message.answer("🔍 Запрашиваю погоду в Санкт-Петербурге...")
    weather_info = get_weather("Saint Petersburg")
    await message.answer(weather_info, parse_mode="Markdown")


# Обработчик кнопки "Помощь"
@dp.message(F.text == "❓ Помощь")
async def help_button(message: types.Message):
    await cmd_help(message)


# Обработчик кнопки "Сменить город"
@dp.message(F.text == "🏙 Сменить город")
async def change_city_button(message: types.Message):
    await message.answer(
        "🏙 Чтобы установить город по умолчанию, используйте команду:\n"
        "`/city <название города>`\n\n"
        "**Пример:** `/city London`\n\n"
        "Или просто отправьте название города, и я покажу погоду в нем.",
        parse_mode="Markdown",
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
        await message.answer(weather_info, parse_mode="Markdown")


# Запуск бота
async def main():
    logger.info("Бот запускается...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
