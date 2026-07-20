from collections import defaultdict, deque
from datetime import datetime

from aiogram import BaseMiddleware
from aiogram.types import Message

user_messages = defaultdict(deque)

LIMIT = 5
INTERVAL = 5


class AntiSpamMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        if not isinstance(event, Message):
            return await handler(event, data)

        if not event.from_user:
            return await handler(event, data)

        now = datetime.now()

        print(f"[SPAM] {event.from_user.id}: {event.text}")

        messages = user_messages[event.from_user.id]
        messages.append(now)

        while messages and (now - messages[0]).total_seconds() > INTERVAL:
            messages.popleft()

        print(f"[SPAM] Количество сообщений: {len(messages)}")

        if len(messages) > LIMIT:
            print("[SPAM] Пользователь превысил лимит!")
            await event.answer("🚫 Не спамь.")
            return

        return await handler(event, data)