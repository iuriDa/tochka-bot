import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

TOKEN = "8706553492:AAEYQd68q2qpJejzsmXOz31i5x_OB7GOEcw"
ADMIN_ID = 6753077789

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class Form(StatesGroup):
    direction = State()
    age = State()
    name = State()
    phone = State()


# ==============================
# START
# ==============================

@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Акробатика")],
            [KeyboardButton(text="Воздушная гимнастика")],
            [KeyboardButton(text="ОФП для взрослых")]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "👋 Добро пожаловать в студию Точка Отрыва!\n\nВыберите направление:",
        reply_markup=keyboard
    )

    await state.set_state(Form.direction)


# ==============================
# Направление
# ==============================

@dp.message(Form.direction)
async def direction(message: types.Message, state: FSMContext):

    await state.update_data(direction=message.text)

    await message.answer("Введите возраст:")

    await state.set_state(Form.age)


# ==============================
# Возраст
# ==============================

@dp.message(Form.age)
async def age(message: types.Message, state: FSMContext):

    await state.update_data(age=message.text)

    await message.answer("Введите имя:")

    await state.set_state(Form.name)


# ==============================
# Имя
# ==============================

@dp.message(Form.name)
async def name(message: types.Message, state: FSMContext):

    await state.update_data(name=message.text)

    phone_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Отправить телефон", request_contact=True)]
        ],
        resize_keyboard=True
    )

    await message.answer(
        "Нажмите кнопку, чтобы отправить телефон:",
        reply_markup=phone_keyboard
    )

    await state.set_state(Form.phone)


# ==============================
# Телефон
# ==============================

@dp.message(Form.phone)
async def phone(message: types.Message, state: FSMContext):

    phone = message.contact.phone_number
    await state.update_data(phone=phone)

    data = await state.get_data()

    user_id = message.from_user.id

    text = f"""
📥 Новая заявка

Направление: {data['direction']}
Возраст: {data['age']}
Имя: {data['name']}
Телефон: {data['phone']}

ID клиента:
{user_id}
"""

    # отправляем админу
    await bot.send_message(
        ADMIN_ID,
        text
    )

    await message.answer(
        "✅ Спасибо!\nАдминистратор скоро свяжется с вами."
    )

    await state.clear()


# ==============================
# ОТВЕТ АДМИНА КЛИЕНТУ
# ==============================

@dp.message()
async def admin_reply(message: types.Message):

    # проверяем что пишет администратор
    if message.from_user.id != ADMIN_ID:
        return

    # проверяем что это ответ
    if not message.reply_to_message:
        return

    reply_text = message.text

    # ищем ID клиента в сообщении
    lines = message.reply_to_message.text.split("\n")

    user_id = None

    for line in lines:
        if "ID клиента" in line:
            continue
        if line.strip().isdigit():
            user_id = int(line.strip())

    if user_id:

        await bot.send_message(
            user_id,
            f"📩 Сообщение от администратора:\n\n{reply_text}"
        )


# ==============================
# запуск
# ==============================

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
