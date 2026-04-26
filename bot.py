import asyncio
import logging
import os
from aiogram import Bot, Dispatcher

from dotenv import load_dotenv

from handlers import router

from db import get_connection, init_db


load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
dp = Dispatcher()
dp.include_router(router)


async def main():
    logging.basicConfig(level=logging.INFO)

    if not TOKEN:
        logging.error("Не найден BOT_TOKEN в переменных окружения")
        raise RuntimeError("Не найден BOT_TOKEN в переменных окружения")
    
    # создаем таблицу в базе данных если нет
    init_db()

    bot = Bot(token=TOKEN)
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())