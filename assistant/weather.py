import requests


def get_weather(city):
    """Получает погоду по названию города с Open-Meteo."""
    try:
        # Получаем координаты города
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=ru&format=json"
        geo_response = requests.get(geo_url).json()

        if "results" not in geo_response or not geo_response["results"]:
            return "Не удалось найти такой город."

        lat = geo_response["results"][0]["latitude"]
        lon = geo_response["results"][0]["longitude"]

        # Получаем прогноз погоды
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=auto&lang=ru"
        weather_response = requests.get(weather_url).json()

        temp = weather_response["current_weather"]["temperature"]
        desc = weather_response["current_weather"]["weathercode"]

        # Описание погоды по коду
        weather_conditions = {
            0: "ясно",
            1: "в основном ясно",
            2: "переменная облачность",
            3: "пасмурно",
            45: "туман",
            48: "иней",
            51: "легкая морось",
            53: "умеренная морось",
            55: "сильная морось",
            61: "легкий дождь",
            63: "умеренный дождь",
            65: "сильный дождь",
            71: "легкий снегопад",
            73: "умеренный снегопад",
            75: "сильный снегопад",
            95: "гроза",
            96: "гроза с небольшим градом",
            99: "гроза с сильным градом",
        }

        desc_text = weather_conditions.get(desc, "неизвестная погода")

        return f"Сейчас в городе {city} {temp}°C, {desc_text}."

    except Exception:
        return "Ошибка при получении погоды."
