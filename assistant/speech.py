import speech_recognition as sr

def recognize_speech():
    import speech_recognition as sr
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🎙 Слушаю...")
        try:
            # timeout - время ожидания начала речи,
            # phrase_time_limit - максимальное время записи фразы (в секундах)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=15)
            text = recognizer.recognize_google(audio, language="ru-RU").lower()
            print(f"🗣 Вы сказали: {text}")
            return text
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return "Ошибка сервиса распознавания"
        except sr.WaitTimeoutError:
            return ""

