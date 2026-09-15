import requests
from playwright.sync_api import sync_playwright

BASE_URL = "https://www.pokemoncenter.com/en-ca/category/tcg-cards"

TARGET_KEYWORDS = [
    "elite trainer box",
    "booster bundle",
]

import os

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


def is_target_product(name):
    name = name.lower()

    return any(
        keyword in name
        for keyword in TARGET_KEYWORDS
    )


def scan_page(page):
    print("Checking Pokémon Center Canada...")

    try:
        page.goto(
            BASE_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        print("Page title:", page.title())
        print("Page URL:", page.url)

        page.wait_for_timeout(5000)

    except Exception as error:
        print("Page loading error:")
        print(error)
        return None

    if page_is_blocked(page):
        print()
        print("⚠️ POKÉMON CENTER ACCESS DENIED")
        print("The website's security system blocked the request.")
        print()
        return "BLOCKED"

    products = []

    links = page.locator("a[href*='/product/']")
    count = links.count()

    print(f"Found {count} product links.")

    for i in range(count):

        try:
            link = links.nth(i)

            name = link.inner_text().strip()
            href = link.get_attribute("href")

            if not name or not href:
                continue

            if not is_target_product(name):
                continue

            if not href.startswith("http"):
                href = "https://www.pokemoncenter.com" + href

            try:
                card = link.locator(
                    "xpath=ancestor::*"
                ).first

                card_text = card.inner_text()

            except Exception:
                card_text = name

            sold_out = "sold out" in card_text.lower()

            products.append(
                {
                    "name": name,
                    "url": href,
                    "available": not sold_out,
                }
            )

        except Exception:
            continue

    return products


def main():

    print()
    print("==========================================")
    print(" Pokémon Center Canada Stock Monitor")
    print(" ETBs + Booster Bundles")
    print(" GitHub Actions mode")
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

        result = scan_page(page)

        if result == "BLOCKED":

            send_telegram(
                "⚠️ Pokémon Center Canada monitor\n\n"
                "Access Denied / Error 15 detected.\n\n"
                "The monitor stopped because "
                "the website security system "
                "blocked the request."
            )

            browser.close()
            return

        if result is None:

            send_telegram(
                "⚠️ Pokémon Center Canada monitor\n\n"
                "The website could not be checked."
            )

            browser.close()
            return

        print()
        print(
            f"Found {len(result)} "
            "ETB/Booster Bundle products."
        )

        for product in result:

            status = (
                "🟢 AVAILABLE"
                if product["available"]
                else "🔴 SOLD OUT"
            )

            print(
                f"{status} - "
                f"{product['name']}"
            )

        browser.close()


if __name__ == "__main__":
    main()
