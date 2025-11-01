from aiogram import types
from bot.keyboards import get_main_keyboard
from config import DEFAULT_CITY
from services.weather_service import weather_service


class MessageHandlers:
    def __init__(self):
        self.default_city = DEFAULT_CITY

    async def cmd_start(self, message: types.Message):
        """Обработчик команды /start"""
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
        weather_info = weather_service.get_weather(self.default_city)
        await message.answer(weather_info)

    async def cmd_help(self, message: types.Message):
        """Обработчик команды /help"""
        help_text = (
            "📖 <b>Помощь по использованию бота</b>\n\n"
            "<b>Команды:</b>\n"
            "• /start - начать работу с ботом\n"
            "• /help - показать эту справку\n"
            "• /weather <город> - погода в указанном городе\n"
            "• /city <город> - установить город по умолчанию\n\n"
            "<b>Примеры:</b>\n"
            "<code>/weather Moscow</code> - погода в Москве\n"
            "<code>/city London</code> - установить Лондон городом по умолчанию"
        )
        await message.answer(help_text)

    async def cmd_weather(self, message: types.Message):
        """Обработчик команды /weather"""
        command_parts = message.text.split()
        if len(command_parts) < 2:
            await message.answer(
                "❌ Укажите город после команды.\n<b>Пример:</b> <code>/weather Moscow</code>"
            )
            return

        city = " ".join(command_parts[1:])
        await message.answer(f"🔍 Запрашиваю погоду для {city}...")
        weather_info = weather_service.get_weather(city)
        await message.answer(weather_info)

    async def cmd_city(self, message: types.Message):
        """Обработчик команды /city"""
        command_parts = message.text.split()
        if len(command_parts) < 2:
            await message.answer(
                "❌ Укажите город после команды.\n<b>Пример:</b> <code>/city London</code>"
            )
            return

        city = " ".join(command_parts[1:])
        weather_info = weather_service.get_weather(city)

        if weather_info.startswith("❌"):
            await message.answer(weather_info)
        else:
            self.default_city = city
            await message.answer(
                f"✅ Город по умолчанию изменен на: <b>{city}</b>\n\n{weather_info}"
            )

    async def weather_spb(self, message: types.Message):
        """Обработчик кнопки 'Погода в СПб'"""
        await message.answer("🔍 Запрашиваю погоду в Санкт-Петербурге...")
        weather_info = weather_service.get_weather("Saint Petersburg")
        await message.answer(weather_info)

    async def help_button(self, message: types.Message):
        """Обработчик кнопки 'Помощь'"""
        await self.cmd_help(message)

    async def change_city_button(self, message: types.Message):
        """Обработчик кнопки 'Сменить город'"""
        await message.answer(
            "🏙 Чтобы установить город по умолчанию, используйте команду:\n"
            "<code>/city &lt;город&gt;</code>\n\n"
            "Или просто отправьте название города, и я покажу погоду в нем."
        )

    async def handle_city_input(self, message: types.Message):
        """Обработчик произвольного ввода города"""
        text = message.text.strip()
        if text not in [
            "🌤 Погода в СПб",
            "❓ Помощь",
            "🏙 Сменить город",
        ] and not text.startswith("/"):
            await message.answer(f"🔍 Запрашиваю погоду для {text}...")
            weather_info = weather_service.get_weather(text)
            await message.answer(weather_info)


# Создаем экземпляр обработчиков
handlers = MessageHandlers()
