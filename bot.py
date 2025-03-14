import logging
import aiohttp
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup  # Используем KeyboardButton
from aiogram.filters import Command
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")

EXCHANGE_API = "https://api.exchangerate-api.com/v4/latest/"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Функция получения курса валют
async def get_exchange_rate(base_currency: str, target_currency: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(EXCHANGE_API + base_currency) as response:
            data = await response.json()
            if target_currency in data["rates"]:
                return data["rates"][target_currency]
            return None

# Создаем меню с кнопками для выбора валют
def create_currency_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)  # Передаем resize_keyboard и one_time_keyboard в параметр
    buttons = [
        KeyboardButton(text="EUR"),  # Кнопка для евро
        KeyboardButton(text="USD"),  # Кнопка для доллара
        KeyboardButton(text="MDL"),  # Кнопка для молдавского лея
    ]
    keyboard.row(*buttons)  # Добавляем кнопки в одну строку
    return keyboard

# Команда /start
@dp.message(Command("start"))
async def start_command(message: Message):
    logging.info(f"User {message.from_user.id} sent '/start'")
    await message.answer(
        "Привет! Выберите валюту для получения курса.",
        reply_markup=create_currency_menu(),  # Передаем клавиатуру
    )
    logging.info(f"Bot response: Привет! Выберите валюту...")

# Обработчик выбора валюты
@dp.message()
async def handle_currency_selection(message: Message):
    selected_currency = message.text
    logging.info(f"User {message.from_user.id} selected currency: {selected_currency}")

    # Получаем курсы выбранной валюты по отношению к другим
    eur_rate = await get_exchange_rate(selected_currency, "EUR")
    usd_rate = await get_exchange_rate(
