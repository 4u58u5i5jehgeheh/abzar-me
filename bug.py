import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import g4f

# راه‌اندازی لاگ‌گیری
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# تابع برای پاسخ به پیام‌ها
def respond(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    response = g4f.ChatCompletion.create(model='gpt-4', messages=[{"role": "user", "content": user_message}])
    update.message.reply_text(response)

# تابع برای شروع ربات
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('سلام! من ربات GPT-4 هستم. بپرسید تا پاسخ بدهم.')

def main() -> None:
    # توکن ربات خود را اینجا قرار دهید
    TOKEN = '7686347838:AAHok7BBglSFxXzXyZdoaV2rQ_99kTdTdww'

    # راه‌اندازی آپدیت‌کننده
    updater = Updater(TOKEN)

    # دریافت دیسپاچر برای ثبت handlerها
    dispatcher = updater.dispatcher

    # ثبت handlerها
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, respond))

    # شروع ربات
    updater.start_polling()

    # اجرا تا زمانی که کاربر ربات را متوقف کند
    updater.idle()

if __name__ == '__main__':
    main()
