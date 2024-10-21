import logging
import nest_asyncio
import requests  # کتابخانه برای ارسال درخواست‌های HTTP
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import g4f
from serpapi import GoogleSearch
import re
from langdetect import detect
import html

# اعمال nest_asyncio
nest_asyncio.apply()

# راه‌اندازی لاگ‌گیری
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# شناسه عددی مالک ربات
OWNER_ID = 1877334512

# کلیدهای API
SERP_API_KEY = '34438daebabf5eb0dce8fac310d38a8555d22b2a66f9ffdc1b551d6ef276211e'
TOMORROW_API_KEY = 'YOUR_TOMORROW_API_KEY'  # کلید API خود را اینجا وارد کنید

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

# تابع برای دریافت اطلاعات آب و هوا از API سرویس Tomorrow
def get_weather(city):
    url = f"https://api.tomorrow.io/v4/timelines"
    params = {
        "location": city,
        "fields": ["temperature", "precipitationType", "windSpeed", "humidity"],
        "timesteps": "1d",  # پیش‌بینی روزانه
        "units": "metric",
        "apikey": TOMORROW_API_KEY
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        try:
            weather_data = data['data']['timelines'][0]['intervals'][0]['values']
            temperature = weather_data['temperature']
            humidity = weather_data['humidity']
            wind_speed = weather_data['windSpeed']
            precip_type = weather_data['precipitationType']
            
            return f"پیش‌بینی آب و هوای {city}:\n" \
                   f"دما: {temperature} درجه سانتی‌گراد\n" \
                   f"رطوبت: {humidity}%\n" \
                   f"سرعت باد: {wind_speed} متر بر ثانیه\n" \
                   f"نوع بارش: {precip_type}"
        except (KeyError, IndexError):
            return "اطلاعات آب و هوا یافت نشد."
    else:
        return "خطایی در دریافت اطلاعات آب و هوا رخ داد."

# تابع برای جستجوی تصاویر
def search_images(query):
    params = {
        "engine": "google",
        "q": query,
        "tbm": "isch",
        "api_key": SERP_API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    
    image_links = []
    for result in results.get('images_results', []):
        image_links.append(result.get('original'))
        if len(image_links) >= 3:
            break
            
    return image_links

# تابع برای تشخیص اینکه آیا پیام حاوی درخواست جستجو است
def is_search_request(message):
    search_keywords = ['جستجو', 'سرچ', 'پیدا کن', 'در اینترنت', 'دنبال کن', 'اطلاعات از اینترنت']
    return any(re.search(keyword, message) for keyword in search_keywords)

# تابع برای تشخیص اینکه آیا کاربر درخواست آب و هوا دارد
def is_weather_request(message):
    weather_keywords = ['آب و هوا', 'وضعیت هوا', 'پیش‌بینی هوا', 'هواشناسی']
    return any(re.search(keyword, message) for keyword in weather_keywords)

# تابع برای تشخیص زبان پیام
def detect_language(text):
    try:
        return detect(text)
    except:
        return 'unknown'

# تابع برای تقسیم پیام‌های طولانی
def split_message(message, max_length=4000):
    return [message[i:i + max_length] for i in range(0, len(message), max_length)]

# تابع برای پاسخ به پیام‌ها
async def respond(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_message = update.message.text.lower()
    language = detect_language(user_message)

    if is_weather_request(user_message):
        city = re.search(r'آب و هوای (.+)', user_message)
        if city:
            city_name = city.group(1).strip()
            weather_info = get_weather(city_name)
            await update.message.reply_text(weather_info)
        else:
            await update.message.reply_text("لطفاً نام شهر را مشخص کنید. مثال: 'آب و هوای تهران'.")
        return

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
            await update.message.reply_text("هیچ تصویری برای این موضوع پیدا نشد.")
        return

    chatgpt_message = f"شما دستیار Amin هستید و به سوال پاسخ می‌دهید: {user_message}"
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
