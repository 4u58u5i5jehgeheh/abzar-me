import logging
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import g4f

# اعمال nest_asyncio
nest_asyncio.apply()

# راه‌اندازی لاگ‌گیری
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# شناسه مالک ربات
OWNER_ID = 1877334512  # شناسه عددی مالک را اینجا وارد کنید
OWNER_NAME = "محمدامین"  # نام مالک ربات

# تابع برای پاسخ به پیام‌ها
async def respond(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_message = update.message.text

    # بررسی مالکیت
    if user_id == OWNER_ID:
        # ساخت پیام برای ارسال به هوش مصنوعی
        chatgpt_message = f"{OWNER_NAME} هستم. تو دستیار من هستی. سوال من: {user_message}"
        response = g4f.ChatCompletion.create(model='gpt-4', messages=[{"role": "user", "content": chatgpt_message}])
        
        await update.message.reply_text(f"{OWNER_NAME}: {response}")  # پاسخ را با نام مالک ارسال کنید
    else:
        await update.message.reply_text("شما مجاز به استفاده از این ربات نیستید.")

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
