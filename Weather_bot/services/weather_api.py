import requests
import logging
from typing import Optional, Dict

import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))
from config.config import WEATHER_API_KEY

class WeatherAPI:
    """Класс для работы с API OpenWeatherMap."""

    BASE_URL = "http://api.openweathermap.org/data/2.5/"

    @staticmethod
    def get_weather(city: str, lang: str = 'ru') -> Optional[Dict]:
        """Получение текущей погоды для указанного города."""
        try:
            response = requests.get(
                f"{WeatherAPI.BASE_URL}weather",
                params={
                    'q': city,
                    'appid': WEATHER_API_KEY,
                    'units': 'metric',
                    'lang': lang
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Weather API error: {e}")
            return None

    @staticmethod
    def get_forecast(city: str, lang: str = 'ru') -> Optional[Dict]:
        """Получение прогноза погоды на 4 дня."""
        try:
            response = requests.get(
                f"{WeatherAPI.BASE_URL}forecast",
                params={
                    'q': city,
                    'appid': WEATHER_API_KEY,
                    'units': 'metric',
                    'lang': lang,
                    'cnt': 4  # Количество дней прогноза
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Weather forecast API error: {e}")
            return None

    @staticmethod
    def format_weather(data: Dict, lang: str = 'ru') -> str:
        """Форматирование данных о текущей погоде в читаемый текст."""
        if not data:
            return "Не удалось получить данные о погоде" if lang == 'ru' else "Failed to get weather data"

        weather = data['weather'][0]
        main = data['main']

        if lang == 'ru':
            return (
                f"Погода в {data['name']}:\n"
                f"🌡 Температура: {main['temp']}°C (ощущается как {main['feels_like']}°C)\n"
                f"☁ {weather['description'].capitalize()}\n"
                f"💧 Влажность: {main['humidity']}%\n"
                f"🌬 Ветер: {data['wind']['speed']} м/с"
            )
        else:
            return (
                f"Weather in {data['name']}:\n"
                f"🌡 Temperature: {main['temp']}°C (feels like {main['feels_like']}°C)\n"
                f"☁ {weather['description'].capitalize()}\n"
                f"💧 Humidity: {main['humidity']}%\n"
                f"🌬 Wind: {data['wind']['speed']} m/s"
            )

    @staticmethod
    def format_forecast(data: Dict, lang: str = 'ru') -> str:
        """Форматирование данных прогноза погоды в читаемый текст."""
        if not data or 'list' not in data:
            return "Не удалось получить прогноз погоды" if lang == 'ru' else "Failed to get weather forecast"

        city = data['city']['name']

        if lang == 'ru':
            result = [f"Прогноз погоды в {city} на ближайшие дни:\n"]
            for item in data['list']:
                date = item['dt_txt']
                weather = item['weather'][0]
                main = item['main']
                result.append(
                    f"\n📅 {date}\n"
                    f"🌡 {main['temp']}°C, {weather['description']}\n"
                    f"💧 Влажность: {main['humidity']}%"
                )
        else:
            result = [f"Weather forecast in {city} for upcoming days:\n"]
            for item in data['list']:
                date = item['dt_txt']
                weather = item['weather'][0]
                main = item['main']
                result.append(
                    f"\n📅 {date}\n"
                    f"🌡 {main['temp']}°C, {weather['description']}\n"
                    f"💧 Humidity: {main['humidity']}%"
                )

        return "\n".join(result)
