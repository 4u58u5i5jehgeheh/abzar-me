import logging
import nest_asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import g4f
from serpapi import GoogleSearch  # کتابخانه SerpApi
import re  # برای تشخیص کلمات مرتبط با جستجو
from langdetect import detect  # برای تشخیص زبان پیام
import html  # برای تصحیح کاراکترهای HTML
import requests  # برای درخواست به API هواشناسی

# اعمال nest_asyncio
nest_asyncio.apply()

# راه‌اندازی لاگ‌گیری
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# شناسه عددی مالک ربات
OWNER_ID = 1877334512  # شناسه عددی مالک را اینجا وارد کنید

# کلید API برای SerpApi
SERP_API_KEY = '34438daebabf5eb0dce8fac310d38a8555d22b2a66f9ffdc1b551d6ef276211e'

# کلید API برای سرویس Tomorrow
TOMORROW_API_KEY = 'yrCD6jDNAXfwV6AyTU30J8isJTDkTgIJ'  # کلید API سرویس هواشناسی Tomorrow

# توکن ربات تلگرام
TELEGRAM_TOKEN = '8110593355:AAHqiN3nNnoQZ7Xwcw2o0m7qxXsYmxy2NVY'

# تابع برای جستجو در اینترنت از طریق SerpApi
def search_internet(query):
    params = {
        "engine": "google",
        "q": query,
        "api_key": SERP_API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    
    search_results = ""
    for i, result in enumerate(results.get('organic_results', []), start=1):
        search_results += f"{i}. {result.get('title')}: {result.get('snippet')}\n"
        if i >= 3:
            break
    
    return search_results if search_results else "هیچ نتیجه‌ای یافت نشد."

# تابع برای دریافت وضعیت آب و هوا از Tomorrow API
def get_weather(city):
    url = f"https://api.tomorrow.io/v4/timelines"
    params = {
        'location': city,
        'fields': ['temperature', 'weatherCode', 'precipitationProbability'],
        'timesteps': 'current',
        'units': 'metric',
        'apikey': TOMORROW_API_KEY
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        weather_data = data['data']['timelines'][0]['intervals'][0]['values']
        temperature = weather_data['temperature']
        weather_code = weather_data['weatherCode']
        precipitation = weather_data['precipitationProbability']
        return f"دمای فعلی: {temperature}°C\nوضعیت آب و هوا: {weather_code}\nاحتمال بارش: {precipitation}%"
    else:
        return "خطایی در دریافت اطلاعات آب و هوا رخ داده است."

# تابع برای تشخیص اینکه آیا پیام حاوی درخواست آب و هوا است
def is_weather_request(message):
    return any(re.search(keyword, message) for keyword in ['هوا', 'آب و هوا', 'وضعیت هوا'])

# تابع برای تشخیص اینکه آیا کاربر می‌خواهد با امین صحبت کند
def wants_to_talk_to_amin(message):
    return any(re.search(keyword, message) for keyword in ['با امین صحبت کنم', 'پیام برای امین', 'به امین بگو'])

# تابع برای تقسیم پیام‌های طولانی
def split_message(message, max_length=4000):
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
    user_message = update.message.text.lower()
    language = detect_language(user_message)

    # بررسی اینکه آیا درخواست آب و هوا است
    if is_weather_request(user_message):
        city = user_message.split()[-1]  # شهر را از پیام کاربر استخراج می‌کنیم
        weather_info = get_weather(city)
        await update.message.reply_text(weather_info)
        return

    # بررسی اینکه آیا کاربر درخواست جستجو دارد
    if is_search_request(user_message):
        search_query = user_message
        search_results = search_internet(search_query)
        chatgpt_message = f"نتایج جستجو برای '{search_query}' به شرح زیر است:\n{search_results}\nلطفاً بر اساس این نتایج، یک پاسخ کامل ارائه بده."
        response = g4f.ChatCompletion.create(model='gpt-4', messages=[{"role": "user", "content": chatgpt_message}])
        split_responses = split_message(response)
        for res in split_responses:
            await update.message.reply_text(html.unescape(res))
        
        image_links = search_images(search_query)
        if image_links:
            await update.message.reply_text("تصاویر مرتبط:")
            for img in image_links:
                await update.message.reply_photo(photo=img)
        else:
            await update.message.reply_text("هیچ تصویری پیدا نشد.")
        return

    # سایر پیام‌ها
    if wants_to_talk_to_amin(user_message):
        await context.bot.send_message(chat_id=OWNER_ID, text=f"کاربر: {update.message.text}")
        await update.message.reply_text("پیام شما به امین ارسال شد.")
        return

    if user_id == OWNER_ID:
        chatgpt_message = f"محمدامین هستم، من سازنده و مالک تو هستم و تو دستیار من روبو هستی. سوال من: {user_message}"
        response = g4f.ChatCompletion.create(model='gpt-4', messages=[{"role": "user", "content": chatgpt_message}])
        split_responses = split_message(response)
        for res in split_responses:
            await update.message.reply_text(html.unescape(f"محمدامین: {res}"))
    else:
        if language == 'fa':
            chatgpt_message = f"شما دستیار Amin هستید و به جای او به این سوال فارسی پاسخ می‌دهید: {user_message}"
        else:
            chatgpt_message = f"You are Amin's assistant and will answer this English question on his behalf: {user_message}"

        response = g4f.ChatCompletion.create(model='gpt-4', messages=[{"role": "user", "content": chatgpt_message}])
        split_responses = split_message(response)
        for res in split_responses:
            await update.message.reply_text(html.unescape(res))

# تابع برای شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('سلام! من ربات GPT-4 هستم. بپرسید تا پاسخ بدهم.')

def main() -> None:
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond))

    application.run_polling()

if __name__ == '__main__':
    main()
