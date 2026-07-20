from google import genai
from config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)


async def correct_english(text: str):
    prompt = f"""
Ты преподаватель английского языка.

Исправь только ошибки в предложении.

Отвечай СТРОГО в таком формате:

✅ Correct:
<исправленный текст>

🇷🇺 Translation:
<перевод на русский>

📝 Mistakes:
- ошибка → исправление
- короткое объяснение (не больше 10 слов)

📚 Example:
одно короткое предложение с правильным использованием.

Не используй:
- длинные объяснения;
- нумерованные списки;
- лишний текст;
- приветствия;
- повторение ответа;
- точка не обязательна.

Текст:
{text}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    return response.text