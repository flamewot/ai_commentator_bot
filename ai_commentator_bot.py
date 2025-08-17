import logging
import openai
import asyncio
import nest_asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext
import os

# Включаем логирование для отладки
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)  # Установим уровень логирования на DEBUG для подробных логов
logger = logging.getLogger(__name__)

# Инициализация OpenAI API
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Генерация комментария через OpenAI
async def generate_comment(post_text: str):
    logger.debug(f"Received post text for comment generation: {post_text}")
    try:
        # Здесь используем метод ChatCompletion.create
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  
            messages=[
                {"role": "system", "content": "Ты токсичный комментатор."},
                {"role": "user", "content": f"Ты не любишь всё и всех. Из интересов у тебя пиво, игра в танки и рыбалка. Напиши токсичный комментарий не длиннее 100 слов к этому сооющению: {post_text}"}
            ]
        )
        # Извлекаем комментарий из ответа
        comment = response['choices'][0]['message']['content'].strip()  # Ответ в поле 'message'
        logger.debug(f"Generated comment: {comment}")
        return comment
    except Exception as e:
        logger.error(f"Error generating comment: {e}")
        return "Бля я сломался сори"

# Реакция на новые посты в канале
async def comment_on_post(update: Update, context: CallbackContext):
    logger.debug("Entering comment_on_post function")
    
    post_text = update.message.text
    logger.debug(f"Received post text: {post_text}")
    
    if post_text:
        logger.info(f"Generating comment for post: {post_text}")
        
        comment_text = await generate_comment(post_text)
        logger.info(f"Generated comment: {comment_text}")
        
        try:
            # Отвечаем именно на сообщение
            await update.message.reply_text(comment_text)
            logger.info("Reply sent successfully.")
        except Exception as e:
            logger.error(f"Error sending reply: {e}")
    else:
        logger.warning("Received an empty post")
    
    # Получаем текст поста
    post_text = update.message.text
    logger.debug(f"Received post text: {post_text}")
    
    if post_text:
        logger.info(f"Generating comment for post: {post_text}")
        
        # Генерация комментария на основе текста поста
        comment_text = await generate_comment(post_text)
        
        # Логируем сгенерированный комментарий
        logger.info(f"Generated comment: {comment_text}")
        

# Создание бота
def create_bot():
    # Токен, который вы получили от BotFather
    token = 'TELEGRAM_TOKEN'  # Замените на свой токен
    
    # Создание объекта Application и передача токена
    application = Application.builder().token(token).build()

    # Обработчик для новых сообщений (постов)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, comment_on_post))

    return application

# Функция для запуска бота
async def main():
    logger.debug("Initializing bot and starting polling")
    application = create_bot()
    logger.info("Starting bot polling...")
    try:
        # Запуск polling
        await application.run_polling(drop_pending_updates=True)
    except Exception as e:
        logger.error(f"Error in bot polling: {e}")

# Применяем nest_asyncio для корректной работы с уже запущенным циклом
nest_asyncio.apply()

# Запуск бота в текущем активном цикле событий
if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        # Если цикл уже запущен, не создаем новый
        if loop.is_running():
            logger.warning("Event loop is already running. Adding task to the current loop.")
            loop.create_task(main())  # Запуск бота в уже работающем цикле
        else:
            logger.debug("No active event loop. Running the bot.")
            loop.run_until_complete(main())  # Запускаем новый цикл, если его нет
    except Exception as e:
        logger.error(f"Error starting event loop: {e}")

