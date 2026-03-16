# ==============================
# Импорт библиотек
# ==============================

import asyncio
import requests  # используется для отправки данных в Google таблицу
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage


# ==============================
# НАСТРОЙКИ
# ==============================

TOKEN = "ВАШ_ТОКЕН_БОТА"  # токен из BotFather
ADMIN_ID = 6753077789     # Telegram ID администратора

# ссылка для записи данных в Google таблицу
# если пока нет — можно оставить пустой
GOOGLE_SCRIPT_URL = "ВСТАВИТЬ_ССЫЛКУ_GOOGLE_SCRIPT"


# ==============================
# Запуск бота
# ==============================

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# ==============================
# Состояния формы (шаги регистрации)
# ==============================

class Form(StatesGroup):
    direction = State()   # направление
    age = State()         # возраст
    name = State()        # имя
    phone = State()       # телефон


# ==============================
# Команда /start
# ==============================

@dp.message(CommandStart())
async def start(message: types.Message, state: FSMContext):

    # создаем клавиатуру выбора направления
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Акробатика")],
            [KeyboardButton(text="Воздушная гимнастика")],
            [KeyboardButton(text="ОФП для взрослых")],
        ],
        resize_keyboard=True
    )

    await message.answer(
        "👋 Добро пожаловать в студию *Точка Отрыва!*\n\n"
        "Выберите направление:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

    # переходим к шагу выбора направления
    await state.set_state(Form.direction)


# ==============================
# Выбор направления
# ==============================

@dp.message(Form.direction)
async def direction(message: types.Message, state: FSMContext):

    await state.update_data(direction=message.text)

    await message.answer("Введите возраст:")

    await state.set_state(Form.age)


# ==============================
# Ввод возраста
# ==============================

@dp.message(Form.age)
async def age(message: types.Message, state: FSMContext):

    await state.update_data(age=message.text)

    await message.answer("Введите имя:")

    await state.set_state(Form.name)


# ==============================
# Ввод имени
# ==============================

@dp.message(Form.name)
async def name(message: types.Message, state: FSMContext):

    await state.update_data(name=message.text)

    # кнопка отправки телефона
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
# Получение телефона
# ==============================

@dp.message(Form.phone)
async def phone(message: types.Message, state: FSMContext):

    # получаем телефон из контакта
    phone = message.contact.phone_number

    await state.update_data(phone=phone)

    # получаем все данные формы
    data = await state.get_data()

    # ссылка на профиль пользователя
    profile_link = f"tg://user?id={message.from_user.id}"

    # формируем сообщение админу
    text = f"""
📥 Новая заявка

Направление: {data['direction']}
Возраст: {data['age']}
Имя: {data['name']}
Телефон: {data['phone']}

Telegram: @{message.from_user.username}
ID: {message.from_user.id}

Открыть профиль:
{profile_link}
"""

    # отправляем заявку администратору
    await bot.send_message(
        ADMIN_ID,
        text
    )

    # ==============================
    # Отправка данных в Google таблицу
    # ==============================

    if GOOGLE_SCRIPT_URL != "":

        payload = {
            "direction": data['direction'],
            "age": data['age'],
            "name": data['name'],
            "phone": data['phone'],
            "telegram_id": message.from_user.id
        }

        try:
            requests.post(GOOGLE_SCRIPT_URL, json=payload)
        except:
            print("Ошибка отправки в Google Sheets")

    # ==============================
    # Ответ пользователю
    # ==============================

    await message.answer(
        "✅ Спасибо!\n\n"
        "Заявка отправлена.\n"
        "Администратор скоро свяжется с вами."
    )

    # очищаем состояние
    await state.clear()


# ==============================
# Запуск бота
# ==============================

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
