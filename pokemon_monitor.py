import requests
import os
from playwright.sync_api import sync_playwright

SEARCH_URLS = [
    "https://www.pokemoncenter.com/en-ca/search/elite-trainer-box",
    "https://www.pokemoncenter.com/en-ca/search/booster-bundle",
]

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


def page_is_blocked(page):
    try:
        title = page.title().lower()
        body = page.locator("body").inner_text().lower()

        blocked_words = [
            "access denied",
            "error 15",
            "request was blocked",
            "blocked by our security service",
            "security service",
        ]

        return any(
            word in title or word in body
            for word in blocked_words
        )

    except Exception:
        return False


def scan_search(page, url):
    print()
    print("Checking:", url)

    try:
        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        page.wait_for_timeout(5000)

        print("Page title:", page.title())
        print("Page URL:", page.url)

    except Exception as error:
        print("Page loading error:")
        print(error)
        return None

    if page_is_blocked(page):
        print("⚠️ ACCESS DENIED")
        return "BLOCKED"

    body_text = page.locator("body").inner_text()

    print("Page text length:", len(body_text))

    return body_text


def main():

    print()
    print("==========================================")
    print(" Pokémon Center Canada Stock Monitor")
    print(" ETBs + Booster Bundles")
    print(" GitHub Actions mode")
    print("==========================================")

    blocked = False

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page(
            locale="en-CA",
            timezone_id="America/Toronto",
        )

        for url in SEARCH_URLS:

            result = scan_search(page, url)

            if result == "BLOCKED":
                blocked = True
                continue

            if result is None:
                continue

            print()
            print("Search page loaded successfully.")
            print("First 1000 characters:")
            print(result[:1000])

        browser.close()

    if blocked:
        send_telegram(
            "⚠️ Pokémon Center Canada monitor\n\n"
            "Access Denied / Error 15 detected.\n\n"
            "The monitor stopped because "
            "the website security system "
            "blocked the request."
        )


if __name__ == "__main__":
    main()
