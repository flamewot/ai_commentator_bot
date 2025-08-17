import os
import logging
import openai
from aiogram import Bot, Dispatcher, types
from aiogram.utils.executor import start_webhook

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.getenv("PORT", 8080))
WEBHOOK_PATH = f"/{TELEGRAM_TOKEN}"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

# Инициализация
openai.api_key = OPENAI_API_KEY
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

@dp.message_handler()
async def comment_on_post(message: types.Message):
    comment = await generate_comment(message.text)
    await message.reply(comment)

if __name__ == "__main__":
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=lambda dp: bot.set_webhook(WEBHOOK_URL),
        on_shutdown=lambda dp: bot.delete_webhook(),
        skip_updates=True,
        host="0.0.0.0",
        port=PORT,
    )
