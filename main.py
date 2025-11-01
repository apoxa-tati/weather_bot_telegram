import asyncio
import logging
from threading import Thread
import time

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from bot.handlers import handlers
from config import PORT, TG_KEY
from web.flask_app import flask_app, run_flask


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_handlers(dp: Dispatcher):
    """Регистрирует все обработчики сообщений"""
    # Команды
    dp.message.register(handlers.cmd_start, Command("start"))
    dp.message.register(handlers.cmd_help, Command("help"))
    dp.message.register(handlers.cmd_weather, Command("weather"))
    dp.message.register(handlers.cmd_city, Command("city"))

    # Кнопки
    dp.message.register(
        handlers.weather_spb, lambda message: message.text == "🌤 Погода в СПб"
    )
    dp.message.register(
        handlers.help_button, lambda message: message.text == "❓ Помощь"
    )
    dp.message.register(
        handlers.change_city_button, lambda message: message.text == "🏙 Сменить город"
    )

    # Произвольный текст (города)
    dp.message.register(handlers.handle_city_input)


async def start_bot():
    """Запускает Telegram бота"""
    logger.info("Инициализация бота...")

    bot = Bot(token=TG_KEY, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Регистрируем обработчики
    setup_handlers(dp)

    logger.info("Запуск Telegram бота...")
    try:
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        raise


def run_bot():
    """Запуск бота в основном event loop"""
    asyncio.run(start_bot())


def main():
    """Основная функция запуска"""
    # Даем время на инициализацию
    time.sleep(2)

    # Запускаем Flask в отдельном потоке как демона
    flask_thread = Thread(target=lambda: run_flask(flask_app, PORT), daemon=True)
    flask_thread.start()

    logger.info(f"Flask запущен на порту {PORT} в фоновом режиме")
    logger.info("Запускаем Telegram бота в основном потоке...")

    # Запускаем бота в основном потоке
    run_bot()


if __name__ == "__main__":
    main()
