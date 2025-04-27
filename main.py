import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import CommandObject
from dotenv import load_dotenv

from model import DB


load_dotenv()

token = os.getenv("BOT_TOKEN")
admin_password = os.getenv("ADMIN_PASSWORD")

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


@dp.message(Command("admin"))
async def admin(message: types.Message, command: CommandObject):
    if db.is_admin(message.chat.id):
        await message.answer("Вы уже являетесь администратором!")
        return
    if not command.args:
        await message.answer("Требуется пароль!")
        return
    args = command.args.split()
    if len(args) != 1:
        await message.answer("Не правильное количество аргументов")
        return
    input_password = args[0]
    if input_password != admin_password:
        await message.answer("Не правильный пароль!")
        return
    db.create_admin(message.chat.id)
    await message.answer("Теперь вы администратор")


@dp.message(Command("startgame"))
async def startgame(message: types.Message):
    if not db.is_admin(message.chat.id):
        return

    if db.is_game_on():
        await message.answer("Игра уже запущена!")
        return

    db.change_game_state(True)
    await message.answer("Игра запущена!")

    for user_id in db.get_all_users_id():
        bot.send_message(user_id, "Игра началась! Поскорее пиши /start, чтобы начать!")

@dp.message(Command("stopgame"))
async def stopgame(message: types.Message):
    if not db.is_admin(message.chat.id):
        return

    if not db.is_game_on():
        await message.answer("Игра не запущена!")
        return
    db.change_game_state(False)
    await message.answer('Игра остановлена!')

    for user_id in db.get_all_users_id():
        bot.send_message(user_id, "Игра закончилась! Ждите начала следующей игры или конца дня.")

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
