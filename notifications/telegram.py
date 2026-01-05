import requests
from config.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"


def send(message):
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        r = requests.post(API_URL, data=payload, timeout=10)

        if r.status_code != 200:
            print("❌ TELEGRAM ERROR:", r.status_code, r.text)

        return r.ok

    except Exception as e:
        print("❌ TELEGRAM EXCEPTION:", e)
        return False
