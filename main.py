import logging
import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

# Включаем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Отправь мне ссылку на видео TikTok, и я помогу тебе его скачать. Используй /cancel для отмены.')

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Операция отменена. Если нужно, просто отправь новую ссылку.')

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text

    # Параметры для скачивания видео
    tik_tok_args = {
        "format": "best",
        "outtmpl": "%(title)s.%(ext)s"
    }

    try:
        if is_url(url) or is_url1(url):
            with yt_dlp.YoutubeDL(tik_tok_args) as ydl:
                info = ydl.extract_info(url, download=True)  # Скачиваем видео
                video_file = ydl.prepare_filename(info)  # Получаем имя файла

                # Проверяем, существует ли файл перед отправкой
                with open(video_file, 'rb') as video:
                    await update.message.reply_video(video)
                    logger.info(f'Отправлено видео: {video_file}')


                os.remove(video_file)  # Удаляем видео после отправки

    except Exception as e:
        logger.error(f'Ошибка: {e}')

def is_url(text: str) -> bool:
    # Проверяем, является ли текст ссылкой
    url_pattern = r'https://vt.tiktok.com'
    return re.match(url_pattern, text) is not None

def is_url1(text: str) -> bool:
    # Проверяем, является ли текст ссылкой
    url_pattern = r'https://www.tiktok.com'
    return re.match(url_pattern, text) is not None

def main() -> None:
    # Замените 'YOUR_TOKEN' на токен вашего бота
    application = ApplicationBuilder().token('7815252894:AAF3NUSKl5IbWAdsdvzeu5X5WshprX80J1g').build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download, block=False))

    # Добавляем фильтр для проверки, является ли сообщение ссылкой
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lambda update, context: download(update, context) if is_url(update.message.text) else None))

    application.run_polling()

if __name__ == '__main__':
    main()
