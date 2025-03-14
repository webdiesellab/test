import logging
import aiohttp
import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")

EXCHANGE_API = "https://api.exchangerate-api.com/v4/latest/USD"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def get_exchange_rate(currency: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(EXCHANGE_API) as response:
            data = await response.json()
            return data["rates"].get(currency.upper(), "Неизвестная валюта")

@dp.message(Command("start"))
async def start_command(message: Message):
    logging.info(f"User {message.from_user.id} sent '/start'")
    await message.answer("Привет! Отправь мне код валюты (например, USD, EUR, RUB), и я покажу курс к доллару.")
    logging.info(f"Bot response: Привет! Отправь мне код валюты...")

@dp.message()
async def send_exchange_rate(message: Message):
    logging.info(f"User {message.from_user.id} sent: {message.text}")
    currency = message.text.strip().upper()
    rate = await get_exchange_rate(currency)
    if rate == "Неизвестная валюта":
        response = "Я не знаю такую валюту. Попробуй USD, EUR, RUB и т.д."
    else:
        response = f"1 USD = {rate} {currency}"
    
    await message.answer(response)
    logging.info(f"Bot response: {response}")

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
