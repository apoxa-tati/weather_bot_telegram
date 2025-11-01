from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Создает основную клавиатуру"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌤 Погода в СПб"), KeyboardButton(text="❓ Помощь")],
            [KeyboardButton(text="🏙 Сменить город")],
        ],
        resize_keyboard=True,
    )
    return keyboard


def get_city_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру для выбора городов (можно расширить)"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Москва"), KeyboardButton(text="Санкт-Петербург")],
            [KeyboardButton(text="Лондон"), KeyboardButton(text="Нью-Йорк")],
            [KeyboardButton(text="🔙 Назад")],
        ],
        resize_keyboard=True,
    )
    return keyboard
