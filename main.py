import asyncio
import logging
import os
import time

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
point_coefficient = 100

logging.basicConfig(level=logging.INFO)
bot = Bot(token)
dp = Dispatcher()
db = DB("quiz.db")

questions_list = db.get_all_questions()


class QuestionStates(StatesGroup):
    waiting_for_question = State()


class AnswerState(StatesGroup):
    waiting_for_answer = State()


@dp.message(Command("records"))
async def on_records(message: types.Message):
    records = db.get_all_records()

    max_length = 10
    for record in records:
        if max_length < len(record[1]):
            max_length = len(record[1])

    for index, record in enumerate(records, 1):
        await message.answer(
            f"{str(index).ljust(2)} | {str(record[1]).ljust(max_length)} | {str(record[2]).ljust(4)}"
        )

@dp.message(Command("close"))


@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    if not db.is_user_exists(message.chat.id):
        db.create_user(message.chat.id, message.from_user.username)

    if not db.is_game_on():
        await message.answer("Дождитесь начала игры! Вам придет уведомление")
        return

    await state.update_data(start_time=time.time())
    await state.update_data(points=0)
    await state.update_data(question_number=0)

    q, a1, a2, a3, a4, _ = questions_list[0]

    kb = [
        [types.KeyboardButton(text=a1), types.KeyboardButton(text=a2)],
        [types.KeyboardButton(text=a3), types.KeyboardButton(text=a4)],
    ]

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        one_time_keyboard=True,
        resize_keyboard=True,
        input_field_placeholder="Выберите вариант ответа",
    )

    await message.answer(q, reply_markup=keyboard)

    await state.set_state(AnswerState.waiting_for_answer)


@dp.message(AnswerState.waiting_for_answer)
async def on_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()

    previous_question = questions_list[data["question_number"]]
    correct_answer_number = previous_question[-1]
    correct_answer = previous_question[correct_answer_number]

    if message.text == correct_answer:
        data["points"] += 1
        await state.update_data(points=data["points"])

    if data["question_number"] == 4:
        await message.answer("Вы ответили на все вопросы!")
        seconds = time.time() - data["start_time"]
        result = data["points"] * point_coefficient // seconds

        await message.answer(f"Ваш счет: {result}")
        db.add_points(message.chat.id, result)
        return

    await state.update_data(question_number=data["question_number"] + 1)

    q, a1, a2, a3, a4, _ = questions_list[data["question_number"]]

    kb = [
        [types.KeyboardButton(text=a1), types.KeyboardButton(text=a2)],
        [types.KeyboardButton(text=a3), types.KeyboardButton(text=a4)],
    ]

    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        one_time_keyboard=True,
        resize_keyboard=True,
        input_field_placeholder="Выберите вариант ответа",
    )

    await message.answer(q, reply_markup=keyboard)


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


@dp.message(Command("questions"))
async def questions(message: types.Message, state: FSMContext):
    if not db.is_admin(message.chat.id):
        return

    if db.is_game_on():
        await message.answer("Сначала остановите игру!")
        return

    db.clear_questions()
    await state.set_state(QuestionStates.waiting_for_question)
    await message.answer(
        "Отправляйте вопросы в формате:\nВопрос|Ответ 1|Ответ 2|Ответ 3|Ответ 4|Номер правильного ответа"
    )


@dp.message(QuestionStates.waiting_for_question)
async def on_question(message: types.Message, state: FSMContext):
    words = message.text.split("|")
    if len(words) != 6:
        await message.answer("Не верный формат вопроса!")
        return

    if not (words[-1].isnumeric() and 1 <= int(words[-1]) <= 4):
        await message.answer("Не корректный номер правильного ответа")
        return

    q = words[0]
    a1, a2, a3, a4 = words[1:5]
    correct_a_number = int(words[5])

    db.create_question(q, a1, a2, a3, a4, correct_a_number)

    if db.get_questions_amount() == 5:
        await state.clear()
        await message.answer("Все вопросы записаны!")
        return

    await message.answer("Вопрос записан! Жду следующий!")


@dp.message(Command("startgame"))
async def startgame(message: types.Message):
    if not db.is_admin(message.chat.id):
        return

    if db.is_game_on():
        await message.answer("Игра уже запущена!")
        return

    if db.get_questions_amount() != 5:
        await message.answer("Не верное количество вопросов!")
        return

    global questions_list
    questions_list = db.get_all_questions()
    db.change_game_state(True)
    await message.answer("Игра запущена!")

    for user_id in db.get_all_users_id():
        await bot.send_message(
            user_id, "Игра началась! Поскорее пиши /start, чтобы начать!"
        )


@dp.message(Command("stopgame"))
async def stopgame(message: types.Message):
    if not db.is_admin(message.chat.id):
        return

    if not db.is_game_on():
        await message.answer("Игра не запущена!")
        return
    db.change_game_state(False)
    await message.answer("Игра остановлена!")

    for user_id in db.get_all_users_id():
        await bot.send_message(
            user_id, "Игра закончилась! Ждите начала следующей игры или конца дня."
        )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
