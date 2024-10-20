import logging
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import g4f
from serpapi import GoogleSearch
import re
import shodan  # کتابخانه Shodan

# اعمال nest_asyncio
nest_asyncio.apply()

# راه‌اندازی لاگ‌گیری
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# شناسه عددی مالک ربات
OWNER_ID = 1877334512  # شناسه عددی مالک را اینجا وارد کنید

# کلید API برای SerpApi
SERP_API_KEY = '34438daebabf5eb0dce8fac310d38a8555d22b2a66f9ffdc1b551d6ef276211e'  # کلید SerpApi شما

# کلید API برای Shodan
SHODAN_API_KEY = 'Y2xOSe6VAHoZXNTeeSoxZgFZt3Qz9WHf'  # کلید Shodan خود را اینجا وارد کنید

# توکن ربات تلگرام
TELEGRAM_TOKEN = '7686347838:AAHok7BBglSFxZdoaV2rQ_99kTdTdww'  # توکن ربات تلگرام شما

# راه‌اندازی Shodan
shodan_api = shodan.Shodan(SHODAN_API_KEY)

# تابع برای جستجو در Shodan
def search_shodan(query):
    try:
        results = shodan_api.search(query)
        search_results = ""
        for result in results['matches'][:3]:  # حداکثر 3 نتیجه نمایش داده شود
            search_results += f"IP: {result['ip_str']}\nData: {result['data']}\n\n"
        return search_results if search_results else "هیچ نتیجه‌ای یافت نشد."
    except Exception as e:
        return f"خطا در جستجو: {str(e)}"

# تابع برای تشخیص اینکه آیا پیام حاوی درخواست جستجو در Shodan است
def is_shodan_request(message):
    return 'ip' in message or 'دستور' in message or 'بررسی' in message  # بررسی عبارات مرتبط

# تابع برای تشخیص اینکه آیا پیام حاوی درخواست جستجو است
def is_search_request(message):
    search_keywords = ['جستجو', 'سرچ', 'پیدا کن', 'در اینترنت', 'دنبال کن', 'اطلاعات از اینترنت']
    return any(re.search(keyword, message) for keyword in search_keywords)

# تابع برای تشخیص اینکه آیا کاربر می‌خواهد با امین صحبت کند
def wants_to_talk_to_amin(message):
    return any(re.search(keyword, message) for keyword in ['با امین صحبت کنم', 'پیام برای امین', 'به امین بگو', 'می‌خواهم با امین صحبت کنم'])

# تابع برای پاسخ به پیام‌ها
async def respond(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_message = update.message.text.lower()  # پیام کاربر را به حروف کوچک تبدیل می‌کنیم

    # بررسی اینکه آیا کاربر درخواست جستجو در Shodan دارد
    if is_shodan_request(user_message):
        search_query = user_message  # کل پیام کاربر را به عنوان عبارت جستجو استفاده می‌کنیم
        search_results = search_shodan(search_query)
        await update.message.reply_text(search_results)
        return

    # بررسی اینکه آیا کاربر درخواست جستجو دارد
    if is_search_request(user_message):
        search_query = user_message  # کل پیام کاربر را به عنوان عبارت جستجو استفاده می‌کنیم
        search_results = search_internet(search_query)
        chatgpt_message = f"نتایج جستجو برای '{search_query}' به شرح زیر است:\n{search_results}\nلطفاً بر اساس این نتایج، یک پاسخ کامل ارائه بده."
        response = g4f.ChatCompletion.create(model='gpt-4', messages=[{"role": "user", "content": chatgpt_message}])
        await update.message.reply_text(response)
        return

    # بررسی اینکه آیا کاربر می‌خواهد با امین صحبت کند
    if wants_to_talk_to_amin(user_message):
        await context.bot.send_message(chat_id=OWNER_ID, text=f"کاربر: {update.message.text}")
        await update.message.reply_text("پیام شما به امین ارسال شد.")
        return

    # اگر کاربر مالک ربات باشد
    if user_id == OWNER_ID:
        chatgpt_message = f"محمدامین هستم، من سازنده و مالک تو هستم و تو دستیار من روبو هستی. سوال من: {user_message}"
        response = g4f.ChatCompletion.create(model='gpt-4', messages=[{"role": "user", "content": chatgpt_message}])
        await update.message.reply_text(f"محمدامین: {response}")
    else:
        chatgpt_message = f"شما دستیار Amin هستید و به جای او به این سوال پاسخ می‌دهید: {user_message}"
        response = g4f.ChatCompletion.create(model='gpt-4', messages=[{"role": "user", "content": chatgpt_message}])
        await update.message
