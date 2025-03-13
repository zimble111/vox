import re
import os
import urllib.parse
from .tts import speak
from .chatgpt import ask_chatgpt
from .weather import get_weather
from.speech import recognize_speech

# Статические команды, прописанные заранее
COMMANDS = {
    "открыть youtube": ["youtube", "ютуб", "открой youtube"],
    "открыть google": ["google", "гугл", "поиск"],
    "погода": ["погода", "какая погода", "температура"],
    "выключить компьютер": ["выключи компьютер", "заверши работу", "отключи пк"]
}


def find_command(text):
    """Ищет статическую команду по заданным ключевым словам."""
    for command, keywords in COMMANDS.items():
        for keyword in keywords:
            if re.search(rf"\b{keyword}\b", text, re.IGNORECASE):
                return command
    return None


def handle_dynamic_youtube(text):
    """
    Обрабатывает команду вида "включи ... на youtube/ютубе" и возвращает URL для поиска на YouTube.
    Пример: "включи сериал кухня на ютубе" → URL для поиска "сериал кухня"
    """
    pattern = r"включи\s+(.+)\s+на\s+(?:youtube|ютубе)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        query = match.group(1).strip()
        encoded_query = urllib.parse.quote_plus(query)
        search_url = "https://www.youtube.com/results?search_query=" + encoded_query
        return search_url, query
    return None, None


def handle_dynamic_spotify_command(text):
    """
    Обрабатывает команду вида "включи [тре(к/ка)]? <название> на spotify/спотифай"
    и пытается воспроизвести трек через AppleScript. Если трек не найден,
    открывает поиск в Spotify.

    Примеры:
      - "воспроизведи трек Imagine на спотифай"
      - "включи дракончик на spotify"
    """
    pattern = r"включи\s+(?:тре(?:к|ка)\s+)?(.+)\s+(?:на|в)\s+(?:spotify|спотифай)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        query = match.group(1).strip()
        from .spotify import search_track, play_track_applescript
        track_uri = search_track(query)
        if track_uri:
            speak(f"Воспроизвожу трек {query} в Spotify")
            play_track_applescript(track_uri)
            return query
        else:
            speak(f"Трек {query} не найден, открываю поиск в Spotify")
            encoded_query = urllib.parse.quote_plus(query)
            spotify_url = f"spotify:search:{encoded_query}"
            os.system(f"open '{spotify_url}'")
            return query
    return None


def handle_command(text):
    """Основной обработчик команд."""
    # Проверяем статические команды
    command = find_command(text)
    if command == "открыть youtube":
        speak("Открываю YouTube")
        os.system("open 'https://www.youtube.com'")
    elif command == "открыть google":
        speak("Открываю Google")
        os.system("open 'https://www.google.com'")
    elif command == "погода":
        speak("Какой город вас интересует?")
        city = recognize_speech()  # Функция для распознавания голоса
        if city:
            weather_info = get_weather(city)
            speak(weather_info)
        else:
            speak("Я не расслышал название города.")
    elif command == "выключить компьютер":
        speak("Выключаю компьютер")
        os.system("shutdown -s -t 10")  # Для Windows; для macOS может понадобиться иной вызов
    else:
        # Сначала проверяем команду для Spotify (автовоспроизведение трека)
        spotify_result = handle_dynamic_spotify_command(text)
        if spotify_result:
            return

        # Затем проверяем команду для YouTube
        youtube_url, youtube_query = handle_dynamic_youtube(text)
        if youtube_url:
            speak(f"Открываю поиск по запросу {youtube_query} на YouTube")
            os.system(f"open '{youtube_url}'")
            return

        # Если ни одна команда не подошла, обращаемся к ChatGPT
        response = ask_chatgpt(text)
        speak(response)
