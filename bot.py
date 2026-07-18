import asyncio

from aiogram import Bot, Dispatcher
from database import init_db

from config import BOT_TOKEN

from handlers.start import router as start_router
from handlers.help import router as help_router
from handlers.filter import router as filter_router
from handlers.warnings import router as warnings_router 
from handlers.resetwarnings import router as resetwarnings_router
from handlers.correct import router as correct_router

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()

# Подключаем роутеры
dp.include_router(start_router)
dp.include_router(help_router)
dp.include_router(warnings_router)
dp.include_router(resetwarnings_router)
dp.include_router(correct_router)
dp.include_router(filter_router)


async def main():
    await init_db()  # Создаём базу данных и таблицу

    print("✅ ModerBot запущен!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())