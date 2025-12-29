import requests


class TelegramNotifier:
    def __init__(self, token, chat_id):
        self.url = f"https://api.telegram.org/bot{token}/sendMessage"
        self.chat_id = chat_id

    def send(self, message):
        requests.post(
            self.url,
            data={
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "Markdown"
            }
        )
