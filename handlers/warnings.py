from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from database import get_warnings

router = Router()


@router.message(Command("warnings"))
async def warnings_command(message: Message):

    member = await message.bot.get_chat_member(
        message.chat.id,
        message.from_user.id
    )

    if member.status not in ("administrator", "creator"):
        await message.answer("❌ Эта команда доступна только администраторам.")
        return

    if not message.reply_to_message:
        await message.answer(
            "❌ Ответьте командой /warnings на сообщение пользователя."
        )
        return

    user = message.reply_to_message.from_user
    warnings = await get_warnings(user.id)

    if warnings == 0:
        next_mute = "5 минут"
    elif warnings == 1:
        next_mute = "15 минут"
    elif warnings == 2:
        next_mute = "40 минут"
    else:
        next_mute = "24 часа"

    await message.answer(
        f"👤 Пользователь: {user.full_name}\n\n"
        f"⚠️ Предупреждений: {warnings}\n"
        f"🔇 Следующий мут: {next_mute}"
    )