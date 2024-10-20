import logging
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import g4f
from serpapi import GoogleSearch  # کتابخانه SerpApi

# اعمال nest_asyncio
nest_asyncio.apply()

# راه‌اندازی لاگ‌گیری
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# شناسه عددی مالک ربات
OWNER_ID = 1877334512  # شناسه عددی مالک را اینجا وارد کنید

# کلید API برای SerpApi
SERP_API_KEY = '34438daebabf5eb0dce8fac310d38a8555d22b2a66f9ffdc1b551d6ef276211e'  # کلید SerpApi خود را اینجا وارد کنید

# تابع برای جستجو در اینترنت از طریق SerpApi
def search_internet(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERP_API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    
    # جمع‌آوری لینک‌های جستجو شده (در این مثال ۳ لینک)
    search_results = ""
    for i, result in enumerate(results.get('organic_results', []), start=1):
        search_results += f"{i}. {result.get('title')}: {result.get('link')}\n"
        if i >= 3:  # حداکثر 3 نتیجه نمایش داده شود
            break
    
    return search_results if search_results else "نتیجه‌ای یافت نشد."

# تابع برای پاسخ به پیام‌ها
async def respond(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_message = update.message.text.lower()  # پیام کاربر را به حروف کوچک تبدیل می‌کنیم

    # بررسی برای درخواست جستجو
    if 'جستجو کن' in user_message or 'سرچ بزن' in user_message:
        search_query = user_message.replace('جستجو کن', '').replace('سرچ بزن', '').strip()
        if search_query:
            search_results = search_internet(search_query)
            await update.message.reply_text(f"نتایج جستجو برای '{search_query}':\n{search_results}")
        else:
            await update.message.reply_text("لطفاً موضوعی برای جستجو وارد کنید.")
        return

    # اگر کاربر مالک ربات باشد
    if user_id == OWNER_ID:
        # پیام یادآوری به ChatGPT قبل از پاسخ برای مالک
        chatgpt_message = f"محمدامین هستم، من سازنده و مالک تو هستم و تو دستیار من روبو هستی. سوال من: {user_message}"
        response = g4f.ChatCompletion.create(model='gpt-4', messages=[{"role": "user", "content": chatgpt_message}])
        
        await update.message.reply_text(f"محمدامین: {response}")  # پاسخ را با یادآوری مالک ارسال کنید
    else:
        # برای سایر کاربران عادی
        chatgpt_message = f"شما دستیار Amin هستید و به جای او به این سوال پاسخ می‌دهید: {user_message}"
        response = g4f.ChatCompletion.create(model='gpt-4', messages=[{"role": "user", "content": chatgpt_message}])
        
        await update.message.reply_text(response)  # پاسخ با یادآوری اینکه دستیار Amin هستید ارسال می‌شود

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
