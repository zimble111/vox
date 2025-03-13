import openai
from .config import CONFIG

openai.api_key = CONFIG.get("openai_api_key")

def ask_chatgpt(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка: {e}"
