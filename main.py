import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

from model import DB


load_dotenv()

token = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
bot = Bot(token)
dp = Dispatcher()
db = DB("quiz.db")

@dp.message(Command("start"))
async def start(message: types.Message):
    if not db.is_user_exists(message.chat.id):
        db.create_user(message.chat.id, message.from_user.username)
    
    # TODO: Проверка запущена ли игра
    # TODO: Начать задавать вопросы


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
