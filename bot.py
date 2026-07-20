# bot.py

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import TOKEN
from handlers import router


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="🏠 Главное меню"),
        BotCommand(command="help", description="❓ Помощь"),
    ]
    await bot.set_my_commands(commands)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    
    dp.include_router(router)
    
    await set_commands(bot)
    
    logging.info("🚀 Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())