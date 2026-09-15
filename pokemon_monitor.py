import os
import requests
from playwright.sync_api import sync_playwright

WALMART_URL = "https://www.walmart.ca/en/browse/toys/trading-cards/pokemon-cards/10011_31745_6000204969672"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def send_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials are missing.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "disable_web_page_preview": False,
        },
        timeout=20,
    )

    response.raise_for_status()


def main():

    print("==========================================")
    print(" Walmart Canada Pokémon Monitor")
    print(" ETBs + Booster Bundles")
    print("==========================================")
    print()

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page(
            locale="en-CA",
            timezone_id="America/Toronto",
        )

        print("Checking Walmart Canada...")

        try:
            page.goto(
                WALMART_URL,
                wait_until="domcontentloaded",
                timeout=60000,
            )

            page.wait_for_timeout(5000)

            print("Page title:", page.title())
            print("Page URL:", page.url)

            body = page.locator("body").inner_text()

            print("Page text length:", len(body))
            print()
            print("First 3000 characters:")
            print(body[:3000])

        except Exception as error:

            print("Page loading error:")
            print(error)

            send_telegram(
                "⚠️ Walmart Canada monitor\n\n"
                "The Walmart page could not be checked."
            )

            browser.close()
            return

        browser.close()


if __name__ == "__main__":
    main()
