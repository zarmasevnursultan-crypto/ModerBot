from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ChatPermissions

from database import reset_warnings

router = Router()


@router.message(Command("resetwarnings"))
async def resetwarnings_command(message: Message):

    member = await message.bot.get_chat_member(
        message.chat.id,
        message.from_user.id
    )

    if member.status not in ("administrator", "creator"):
        await message.answer("❌ Эта команда доступна только администраторам.")
        return

    if not message.reply_to_message:
        await message.answer(
            "❌ Ответьте этой командой на сообщение пользователя."
        )
        return

    user = message.reply_to_message.from_user

    await reset_warnings(user.id)

    await message.bot.restrict_chat_member(
        chat_id=message.chat.id,
        user_id=user.id,
        permissions=ChatPermissions(
            can_send_messages=True,
            can_send_audios=True,
            can_send_documents=True,
            can_send_photos=True,
            can_send_videos=True,
            can_send_video_notes=True,
            can_send_voice_notes=True,
            can_send_polls=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
            can_change_info=False,
            can_invite_users=True,
            can_pin_messages=False,
        )
    )

    await message.answer(
        f"✅ Предупреждения пользователя {user.full_name} сброшены.\n"
        f"🔓 Мут снят."
    )