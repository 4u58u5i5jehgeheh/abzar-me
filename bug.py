import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import g4f

# راه‌اندازی لاگ‌گیری
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# تابع برای پاسخ به پیام‌ها
async def respond(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    response = g4f.ChatCompletion.create(model='gpt-4', messages=[{"role": "user", "content": user_message}])
    await update.message.reply_text(response)

# تابع برای شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('سلام! من ربات GPT-4 هستم. بپرسید تا پاسخ بدهم.')

def main() -> None:
    # توکن ربات خود را اینجا قرار دهید
    TOKEN = '7686347838:AAHok7BBglSFxXzXyZdoaV2rQ_99kTdTdww'

    # راه‌اندازی برنامه
    application = ApplicationBuilder().token(TOKEN).build()

    # ثبت handlerها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond))

    # شروع ربات
    application.run_polling()

if __name__ == '__main__':
    main()
