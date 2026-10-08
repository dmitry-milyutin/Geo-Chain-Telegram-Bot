import requests
import wikipedia
from mistralai.client import Mistral

from config import WEATHER_API, MISTRAL_API_KEY

    
# weather_icons, get_weather, ask_ai, get_wiki_info

wikipedia.set_lang("en")
wikipedia.set_user_agent("CitiesTelegramBot/1.0 (https://github.com/dmitry-milyutin)")

weather_icons = {
    "01d": "☀️", "01n": "🌕", "02d": "🌤️", "02n": "🌥️", "03d": "⛅", "03n": "☁️",
    "04d": "🌥️", "04n": "☁️", "09d": "🌧️", "09n": "🌧️", "10d": "🌦️", "10n": "🌧️",
    "11d": "⛈️", "11n": "🌩️", "13d": "❄️", "13n": "🌨️", "50d": "🌫️", "50n": "🌫️"
}

def get_weather(lat, long):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={long}&APPID={WEATHER_API}&units=metric"
        response = requests.get(url, timeout=10)
        dic = response.json()
        temp = dic["main"]["temp"]
        feels_like = dic["main"]["feels_like"]
        main = dic["weather"][0]["main"]
        sea_level = dic["main"].get("sea_level", "N/A")
        clouds = dic["clouds"]["all"]
        emoji_id = dic["weather"][0]["icon"]
        return temp, feels_like, main, sea_level, clouds, emoji_id
    except Exception:
        return None

def ask_ai(prompt):
    try:
        api_key = MISTRAL_API_KEY
        # model = "mistral-large-latzest"
        model = "mistral-small-latest"

        client = Mistral(api_key=api_key)

        chat_response = client.chat.complete(
            model = model,
            messages = [
                {
                    "role": "user",
                    "content": prompt,
                },
            ]
        )
        return chat_response.choices[0].message.content
    except Exception as e:
        print("AI error:", e)
        return None


def get_wiki_info(city):
    try:
        search_results = wikipedia.search(city)
        if not search_results:
            return None, None
        title = search_results[0]
        city_page = wikipedia.page(title, auto_suggest=False)
        summary = wikipedia.summary(title, sentences=3, auto_suggest=False)
        return summary, city_page.url
    except Exception:
        return None, None