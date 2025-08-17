import os
import logging
import openai
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.utils.executor import start_webhook
import asyncio

# Настройки
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.getenv("PORT", 8080))
WEBHOOK_PATH = f"/{TELEGRAM_TOKEN}"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"
WEBAPP_HOST = "0.0.0.0"

# Инициализация
openai.api_key = OPENAI_API_KEY
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Генерация комментария
async def generate_comment(post_text: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты токсичный комментатор."},
                {"role": "user",
                 "content": f"Ты не любишь всё и всех. Из интересов у тебя пиво, игра в танки и рыбалка. "
                            f"Напиши токсичный комментарий не длиннее 100 слов к этому сообщению: {post_text}"}
            ],
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"Ошибка генерации комментария: {e}")
        return "Бля я сломался сори"

# Обработчик сообщений
@dp.message_handler()
async def comment_on_post(message: Message):
    post_text = message.text
    comment = await generate_comment(post_text)
    await message.reply(comment)

# Запуск webhook
async def on_startup(dispatcher: Dispatcher):
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown(dispatcher: Dispatcher):
    await bot.delete_webhook()

if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=PORT,
    )
