import logging
import aiohttp
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
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

# Создаём inline кнопки для выбора валют
def create_currency_menu():
    keyboard = InlineKeyboardMarkup(row_width=3)
    buttons = [
        InlineKeyboardButton(text="EUR", callback_data="EUR"),
        InlineKeyboardButton(text="USD", callback_data="USD"),
        InlineKeyboardButton(text="MDL", callback_data="MDL"),
    ]
    keyboard.add(*buttons)
    return keyboard

# Команда /start
@dp.message(Command("start"))
async def start_command(message: Message):
    logging.info(f"User {message.from_user.id} sent '/start'")
    await message.answer(
        "Привет! Выберите валюту для получения курса.",
        reply_markup=create_currency_menu(),
    )
    logging.info(f"Bot response: Привет! Выберите валюту...")

# Обработчик выбора валюты
@dp.callback_query()
async def handle_currency_selection(callback_query: types.CallbackQuery):
    selected_currency = callback_query.data
    logging.info(f"User {callback_query.from_user.id} selected currency: {selected_currency}")

    # Получаем курсы выбранной валюты по отношению к другим
    eur_rate = await get_exchange_rate(selected_currency, "EUR")
    usd_rate = await get_exchange_rate(selected_currency, "USD")

    if eur_rate is None or usd_rate is None:
        await callback_query.answer("Не удалось получить курс для выбранной валюты.")
        return

    response = f"Курс для {selected_currency}:\n"
    response += f"1 {selected_currency} = {eur_rate} EUR\n"
    response += f"1 {selected_currency} = {usd_rate} USD"

    # Отправляем результат
    await callback_query.message.answer(response)
    await callback_query.answer()

# Главная функция для запуска
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
