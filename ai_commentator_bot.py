import logging
import os
import openai
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# 🔐 Берём токены из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PORT = int(os.getenv("PORT", 8080))  # Render сам подставит порт

openai.api_key = OPENAI_API_KEY

# Логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)
logger = logging.getLogger(__name__)


# Генерация комментария
async def generate_comment(post_text: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты токсичный комментатор."},
                {
                    "role": "user",
                    "content": f"Ты не любишь всё и всех. Из интересов у тебя пиво, игра в танки и рыбалка. "
                               f"Напиши токсичный комментарий не длиннее 100 слов к этому сообщению: {post_text}",
                },
            ],
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"Ошибка генерации комментария: {e}")
        return "Бля я сломался сори"


# Обработчик сообщений
async def comment_on_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post_text = update.message.text if update.message else None
    if not post_text:
        return

    logger.info(f"Новый пост: {post_text}")
    comment_text = await generate_comment(post_text)

    try:
        await update.message.reply_text(comment_text)
        logger.info("Ответ отправлен успешно.")
    except Exception as e:
        logger.error(f"Ошибка при отправке ответа: {e}")


# 🚀 Запуск через webhook (Render)
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, comment_on_post)
    )

    # Render требует webhook, а не polling
    application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TELEGRAM_TOKEN,
        webhook_url=f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}/{TELEGRAM_TOKEN}",
    )


if __name__ == "__main__":
    main()
