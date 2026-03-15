import asyncio
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


@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Акробатика")],
            [KeyboardButton(text="Воздушная гимнастика")],
            [KeyboardButton(text="ОФП для взрослых")],
        ],
        resize_keyboard=True
    )

    await message.answer(
        "👋 Добро пожаловать в студию Точка Отрыва!\n\nВыберите направление:",
        reply_markup=keyboard
    )

    await state.set_state(Form.direction)


@dp.message(Form.direction)
async def direction(message: types.Message, state: FSMContext):

    await state.update_data(direction=message.text)

    await message.answer("Введите возраст ребенка:")

    await state.set_state(Form.age)


@dp.message(Form.age)
async def age(message: types.Message, state: FSMContext):

    await state.update_data(age=message.text)

    await message.answer("Введите имя ребенка:")

    await state.set_state(Form.name)


@dp.message(Form.name)
async def age(message: types.Message, state: FSMContext):

    await state.update_data(age=message.text)

    await message.answer("Введите Ваше имя:")

    await state.set_state(Form.name)


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


@dp.message(Form.phone)
async def phone(message: types.Message, state: FSMContext):

    phone = message.contact.phone_number

    await state.update_data(phone=phone)

    data = await state.get_data()

    text = (
        "📥 Новая заявка\n\n"
        f"Направление: {data['direction']}\n"
        f"Возраст: {data['age']}\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}"
    )

    await bot.send_message(
        ADMIN_ID,
        text
    )

    await message.answer(
        "✅ Спасибо! Заявка отправлена.\nАдминистратор скоро свяжется с вами."
    )

    await state.clear()


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
