import os

from dotenv import load_dotenv


# Загружаем переменные окружения
load_dotenv()

# Получаем токены
TG_KEY = os.getenv("TG_KEY")
API_KEY = os.getenv("API_KEY")
PORT = int(os.getenv("PORT", 10000))

# Валидация конфигурации
if not TG_KEY:
    raise ValueError("Не найден TG_KEY в переменных окружения")
if not API_KEY:
    raise ValueError("Не найден API_KEY в переменных окружения")

# Константы
DEFAULT_CITY = "Saint Petersburg"
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
