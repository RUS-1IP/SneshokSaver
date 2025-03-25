import logging
import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = 'ВАШ_ТОКЕН'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Привет! Отправь мне ссылку на видео TikTok, и я помогу тебе его скачать. Используй /cancel для отмены.')

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Операция отменена. Если нужно, просто отправь новую ссылку.')

async def download(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text

    tik_tok_args = {
        "format": "best",
        "outtmpl": "%(title)s.%(ext)s"
    }

    try:
        if is_url(url) or is_url1(url):
            with yt_dlp.YoutubeDL(tik_tok_args) as ydl:
                info = ydl.extract_info(url, download=True)  
                video_file = ydl.prepare_filename(info)  

                with open(video_file, 'rb') as video:
                    await update.message.reply_video(video)
                    logger.info(f'Отправлено видео: {video_file}')


                os.remove(video_file) 

    except Exception as e:
        logger.error(f'Ошибка: {e}')

def is_url(text: str) -> bool:
    url_pattern = r'https://vt.tiktok.com'
    return re.match(url_pattern, text) is not None

def is_url1(text: str) -> bool:
    url_pattern = r'https://www.tiktok.com'
    return re.match(url_pattern, text) is not None

def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download, block=False))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, lambda update, context: download(update, context) if is_url(update.message.text) else None))

    application.run_polling()

if __name__ == '__main__':
    main()
