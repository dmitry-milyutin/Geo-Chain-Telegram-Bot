import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEATHER_API = os.getenv("WEATHER_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")


for key in [API_TOKEN, WEATHER_API, MISTRAL_API_KEY]:
    if not key:
        raise SystemExit(f"Missing keys: copy .env.example to .env and fill in your keys.")