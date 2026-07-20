from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

from aiogram import BaseMiddleware
from aiogram.types import Message, ChatPermissions

user_messages = defaultdict(deque)

LIMIT = 5          # максимум сообщений
INTERVAL = 5       # за сколько секунд
MUTE_MINUTES = 5   # мут


class AntiSpamMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        if not isinstance(event, Message):
            return await handler(event, data)

        if not event.from_user:
            return await handler(event, data)

        now = datetime.now()

        messages = user_messages[event.from_user.id]
        messages.append(now)

        while messages and (now - messages[0]).total_seconds() > INTERVAL:
            messages.popleft()

        if len(messages) > LIMIT:
            try:
                # Удаляем сообщение
                await event.delete()

                # Выдаем мут
                until_date = datetime.now(timezone.utc) + timedelta(minutes=MUTE_MINUTES)

                await event.bot.restrict_chat_member(
                    chat_id=event.chat.id,
                    user_id=event.from_user.id,
                    permissions=ChatPermissions(
                        can_send_messages=False
                    ),
                    until_date=until_date
                )

                # Очищаем историю сообщений пользователя
                user_messages[event.from_user.id].clear()

                # Сообщение в чат
                await event.answer(
                    f"🚫 {event.from_user.full_name} получил мут на {MUTE_MINUTES} минут за спам."
                )

            except Exception as e:
                print("Ошибка AntiSpam:", e)

            return

        return await handler(event, data)