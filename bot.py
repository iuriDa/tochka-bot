import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
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
            [KeyboardButton(text="Скиппинг")],
            [KeyboardButton(text="ОФП для взрослых")]
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
    await message.answer("Введите возраст:")
    await state.set_state(Form.age)


@dp.message(Form.age)
async def age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Введите ФИО:")
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
    # ✅ Защита: если контакт не был отправлен
    if not message.contact:
        await message.answer("Пожалуйста, используйте кнопку для отправки телефона.")
        return

    phone_number = message.contact.phone_number
    await state.update_data(phone=phone_number)
    data = await state.get_data()
    user_id = message.from_user.id

    # ✅ ID клиента вынесен в отдельную строку с чётким префиксом
    text = (
        f"📥 Новая заявка\n\n"
        f"Направление: {data['direction']}\n"
        f"Возраст: {data['age']}\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n\n"
        f"CLIENT_ID:{user_id}"   # <-- без пробелов, легко парсить
    )

    await bot.send_message(ADMIN_ID, text)
    await message.answer(
        "✅ Спасибо! Администратор скоро свяжется с вами.",
        reply_markup=ReplyKeyboardRemove()
    )
    await state.clear()


@dp.message()
async def admin_reply(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    if not message.reply_to_message:
        return

    original_text = message.reply_to_message.text
    if not original_text:
        return

    user_id = None

    # ✅ Ищем строку с чётким префиксом CLIENT_ID:
    for line in original_text.split("\n"):
        line = line.strip()
        if line.startswith("CLIENT_ID:"):
            try:
                user_id = int(line.split(":")[1])
            except (IndexError, ValueError):
                pass
            break

    if not user_id:
        await message.reply("❌ Не удалось найти ID клиента в заявке")
        return

    await bot.send_message(
        user_id,
        f"📩 Ответ от администратора:\n\n{message.text}"
    )
    await message.reply("✅ Сообщение отправлено клиенту")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
