from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from ai import correct_english

router = Router()


@router.message(Command("correct"))
async def cmd_correct(message: Message):

    text = message.text.replace("/correct", "").strip()

    if not text:
        await message.answer(
            "Например:\n"
            "/correct Hello everyone"
        )
        return

    answer = await correct_english(text)

    await message.answer(answer)