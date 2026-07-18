from datetime import datetime, timedelta, timezone

from aiogram import Router
from aiogram.types import Message, ChatPermissions

from database import add_warning
from filters.bad_words import BAD_WORDS

router = Router()


@router.message()
async def filter_message(message: Message):
    print("Фильтр получил:", message.text)

    if not message.text:
        return

    # Пропускаем все команды
    if message.text.startswith("/"):
        return

    text = message.text.lower()
    print("Получено сообщение:", text)

    for word in BAD_WORDS:
        print("Проверяю:", word)
        if word in text:
            print("НАЙДЕНО!")

            # Удаляем сообщение
            await message.delete()

            # Добавляем предупреждение
            warnings = await add_warning(message.from_user.id)
            print(f"Нарушений: {warnings}")

            # Определяем время мута
            if warnings == 1:
                mute_minutes = 5
            elif warnings == 2:
                mute_minutes = 15
            elif warnings == 3:
                mute_minutes = 40
            else:
                mute_minutes = 24 * 60

            # Время окончания мута
            until_date = datetime.now(timezone.utc) + timedelta(minutes=mute_minutes)

            # Выдаём мут
            try:
                await message.bot.restrict_chat_member(
                    chat_id=message.chat.id,
                    user_id=message.from_user.id,
                    permissions=ChatPermissions(
                        can_send_messages=False
                    ),
                    until_date=until_date
                )
                print("✅ Мут выдан!")

            except Exception as e:
                print("❌ Ошибка при выдаче мута:", e)

            # Сообщение в чат
            await message.answer(
                f"⚠️ {message.from_user.full_name}, сообщение удалено за использование запрещённых слов.\n"
                f"🔇 Выдан мут на {mute_minutes} минут."
            )

            return