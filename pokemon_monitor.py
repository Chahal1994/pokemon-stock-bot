import os
import requests
from datetime import datetime, timezone

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def telegram_request(method, data=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"

    response = requests.post(
        url,
        data=data or {},
        timeout=20,
    )

    response.raise_for_status()
    return response.json()


def send_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials are missing.")
        return

    telegram_request(
        "sendMessage",
        {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
        },
    )


def check_telegram():
    result = telegram_request("getMe")

    bot_name = result["result"].get("first_name", "Telegram bot")

    print("Telegram connection successful.")
    print("Bot:", bot_name)

    send_message(
        "🤖 Pokémon Stock Monitor\n\n"
        "Telegram connection is working! ✅\n\n"
        f"Checked: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
    )


def main():
    print("==========================================")
    print(" Pokémon Telegram Stock Monitor")
    print("==========================================")
    print()

    check_telegram()


if __name__ == "__main__":
    main()
