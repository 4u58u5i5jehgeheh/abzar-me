import logging
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import g4f
from serpapi import GoogleSearch  # کتابخانه SerpApi
import re  # برای تشخیص کلمات مرتبط با جستجو
from langdetect import detect  # برای تشخیص زبان پیام
import html  # برای تصحیح کاراکترهای HTML

# اعمال nest_asyncio
nest_asyncio.apply()

# راه‌اندازی لاگ‌گیری
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# شناسه عددی مالک ربات
OWNER_ID = 1877334512  # شناسه عددی مالک را اینجا وارد کنید

# کلید API برای SerpApi
SERP_API_KEY = '34438daebabf5eb0dce8fac310d38a8555d22b2a66f9ffdc1b551d6ef276211e'  # کلید SerpApi شما

# توکن ربات تلگرام
TELEGRAM_TOKEN = '8110593355:AAHqiN3nNnoQZ7Xwcw2o0m7qxXsYmxy2NVY'  # توکن ربات تلگرام شما

# تابع برای جستجو در اینترنت از طریق SerpApi
def search_internet(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERP_API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    
    # جمع‌آوری متن نتایج جستجو
    search_results = ""
    for i, result in enumerate(results.get('organic_results', []), start=1):
        search_results += f"{i}. {result.get('title')}: {result.get('snippet')}\n"
        if i >= 3:  # حداکثر 3 نتیجه نمایش داده شود
            break
    
    return search_results if search_results else "هیچ نتیجه‌ای یافت نشد."

# تابع برای تشخیص اینکه آیا پیام حاوی درخواست جستجو است
def is_search_request(message):
    search_keywords = ['جستجو', 'سرچ', 'پیدا کن', 'در اینترنت', 'دنبال کن', 'اطلاعات از اینترنت']
    return any(re.search(keyword, message) for keyword in search_keywords)

# تابع برای تشخیص اینکه آیا کاربر می‌خواهد با امین صحبت کند
def wants_to_talk_to_amin(message):
    return any(re.search(keyword, message) for keyword in ['با امین صحبت کنم', 'پیام برای امین', 'به امین بگو', 'می‌خواهم با امین صحبت کنم'])

# تابع برای تقسیم پیام‌های طولانی
def split_message(message, max_length=4000):
    # تقسیم پیام‌ها به چند بخش اگر طول پیام بیشتر از حداکثر مجاز باشد
    return [message[i:i + max_length] for i in range(0, len(message), max_length)]

# تابع برای تشخیص زبان پیام
def detect_language(text):
    try:
        return detect(text)
    except:
        return 'unknown'

# تابع برای پاسخ به پیام‌ها
async def respond(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_message = update.message.text.lower()  # پیام کاربر را به حروف کوچک تبدیل می‌کنیم
    language = detect_language(user_message)  # تشخیص زبان پیام

    # بررسی اینکه آیا کاربر درخواست جستجو دارد
    if is_search_request(user_message):
        search_query = user_message  # کل پیام کاربر را به عنوان عبارت جستجو استفاده می‌کنیم
        search_results = search_internet(search_query)
        # ارسال نتایج جستجو به ChatGPT برای تحلیل
        chatgpt_message = f"نتایج جستجو برای '{search_query}' به شرح زیر است:\n{search_results}\nلطفاً بر اساس این نتایج، یک پاسخ کامل ارائه بده."
        response = g4f.ChatCompletion.create(model='gpt-4', messages=[{"role": "user", "content": chatgpt_message}])
        split_responses = split_message(response)  # تقسیم پاسخ‌های بلند
        for res in split_responses:
            await update.message.reply_text(html.unescape(res))  # تصحیح متن و ارسال بخش‌های پاسخ به کاربر
        return

    # بررسی اینکه آیا کاربر می‌خواهد با امین صحبت کند
    if wants_to_talk_to_amin(user_message):
        # ارسال پیام به امین
        await context.bot.send_message(chat_id=OWNER_ID, text=f"کاربر: {update.message.text}")
        await update.message.reply_text("پیام شما به امین ارسال شد.")
        return

    # اگر کاربر مالک ربات باشد
    if user_id == OWNER_ID:
        # پیام یادآوری به ChatGPT قبل از پاسخ برای مالک
        chatgpt_message = f"محمدامین هستم، من سازنده و مالک تو هستم و تو دستیار من روبو هستی. سوال من: {user_message}"
        response = g4f.ChatCompletion.create(model='gpt-4', messages=[{"role": "user", "content": chatgpt_message}])
        
        split_responses = split_message(response)  # تقسیم پاسخ‌های بلند
        for res in split_responses:
            await update.message.reply_text(html.unescape(f"محمدامین: {res}"))  # تصحیح متن و ارسال پاسخ را با یادآوری مالک ارسال کنید
    else:
        # برای سایر کاربران عادی
        if language == 'fa':
            chatgpt_message = f"شما دستیار Amin هستید و به جای او به این سوال فارسی پاسخ می‌دهید: {user_message}"
        else:
            chatgpt_message = f"You are Amin's assistant and will answer this English question on his behalf: {user_message}"

        response = g4f.ChatCompletion.create(model='gpt-4', messages=[{"role": "user", "content": chatgpt_message}])
        
        split_responses = split_message(response)  # تقسیم پاسخ‌های بلند
        for res in split_responses:
            await update.message.reply_text(html.unescape(res))  # تصحیح متن و ارسال بخش‌های پاسخ به کاربر

# تابع برای شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('سلام! من ربات GPT-4 هستم. بپرسید تا پاسخ بدهم.')

def main() -> None:
    # راه‌اندازی برنامه
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # ثبت handlerها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond))

    # شروع ربات
    application.run_polling()

if __name__ == '__main__':
    main()
