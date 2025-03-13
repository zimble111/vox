# assistant/tts.py
import asyncio
import edge_tts
import tempfile
import os
from playsound import playsound
import multiprocessing

# Глобальная переменная для хранения текущего процесса синтеза речи
CURRENT_TTS_PROCESS = None

def _speak(text):
    async def run_tts():
        communicate = edge_tts.Communicate(text, voice="ru-RU-SvetlanaNeural")
        audio_data = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.extend(chunk["data"])
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            f.write(audio_data)
            temp_filename = f.name
        playsound(temp_filename)
        os.remove(temp_filename)
    asyncio.run(run_tts())

def speak(text):
    global CURRENT_TTS_PROCESS
    # Запускаем TTS в отдельном процессе
    p = multiprocessing.Process(target=_speak, args=(text,))
    p.start()
    CURRENT_TTS_PROCESS = p
    return p
