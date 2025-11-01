from datetime import datetime

from config import API_KEY, WEATHER_API_URL
import requests


class WeatherService:
    def __init__(self):
        self.api_key = API_KEY
        self.base_url = WEATHER_API_URL

    def get_weather(self, city: str) -> str:
        """Получает данные о погоде для указанного города"""
        try:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",
                "lang": "ru",
            }

            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()

            return self._format_weather_data(data, city)

        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                return f"❌ Город '{city}' не найден. Проверьте правильность написания."
            else:
                return f"❌ Ошибка при получении данных: {e}"
        except Exception as e:
            return f"❌ Ошибка: {e}"

    def _format_weather_data(self, data: dict, city: str) -> str:
        """Форматирует данные о погоде в читаемый вид"""
        weather_info = f"🌤 <b>Погода в {city}</b>\n\n"
        weather_info += (
            f"• <b>Состояние:</b> {data['weather'][0]['description'].capitalize()}\n"
        )
        weather_info += f"• <b>Температура:</b> {data['main']['temp']} °C\n"
        weather_info += f"• <b>Ощущается как:</b> {data['main']['feels_like']} °C\n"
        weather_info += f"• <b>Влажность:</b> {data['main']['humidity']}%\n"
        weather_info += f"• <b>Давление:</b> {data['main']['pressure']} гПа\n"
        weather_info += f"• <b>Скорость ветра:</b> {data['wind']['speed']} м/с\n"

        # Время заката
        sunset_timestamp = data["sys"]["sunset"]
        sunset_time = datetime.fromtimestamp(sunset_timestamp).strftime("%H:%M:%S")
        weather_info += f"• <b>Закат:</b> {sunset_time}\n"

        return weather_info


# Создаем экземпляр сервиса для импорта
weather_service = WeatherService()
