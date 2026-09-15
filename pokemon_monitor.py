import time
import requests

from playwright.sync_api import sync_playwright

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


# Pokémon Center Canada
BASE_URL = "https://www.pokemoncenter.com/en-ca/category/tcg-cards"

# Check every 10 minutes
CHECK_INTERVAL = 600

# Only monitor these product types
TARGET_KEYWORDS = [
    "elite trainer box",
    "booster bundle",
]


def send_telegram(message):
    """Send a Telegram message."""

    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    try:
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

    except Exception as error:
        print("Telegram error:", error)


def page_is_blocked(page):
    """Detect Pokémon Center security/access-denied pages."""

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

        for word in blocked_words:

            if word in title or word in body:
                return True

    except Exception:
        pass

    return False


def is_target_product(name):
    """Check for ETBs and Booster Bundles."""

    name = name.lower()

    return any(
        keyword in name
        for keyword in TARGET_KEYWORDS
    )


def scan_page(page):
    """Scan the catalog page."""

    print("Checking Pokémon Center Canada...")

    try:

        page.goto(
            BASE_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        page.wait_for_timeout(5000)

    except Exception as error:

        print("Page loading error:")
        print(error)

        return None


    # Check whether Pokémon Center blocked us
    if page_is_blocked(page):

        print()
        print("⚠️ POKÉMON CENTER ACCESS DENIED")
        print("The website's security system blocked the request.")
        print()

        return "BLOCKED"


    products = []

    # Look for product links
    links = page.locator(
        "a[href*='/product/']"
    )

    count = links.count()

    print(
        f"Found {count} product links."
    )


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

                href = (
                    "https://www.pokemoncenter.com"
                    + href
                )


            # Get surrounding text
            try:

                card = link.locator(
                    "xpath=ancestor::*"
                ).first

                card_text = card.inner_text()

            except Exception:

                card_text = name


            sold_out = (
                "sold out"
                in card_text.lower()
            )


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
    print(" Safe monitoring mode")
    print("==========================================")
    print()

    previous_state = {}

    blocked_alert_sent = False

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page(
            locale="en-CA",
            timezone_id="America/Toronto",
        )


        while True:

            result = scan_page(page)


            # Website blocked us
            if result == "BLOCKED":

                if not blocked_alert_sent:

                    send_telegram(
                        "⚠️ Pokémon Center Canada monitor\n\n"
                        "Access Denied / Error 15 detected.\n\n"
                        "The monitor has stopped checking "
                        "to avoid repeatedly triggering "
                        "the site's security system."
                    )

                    blocked_alert_sent = True


                print()
                print(
                    "Monitoring paused because "
                    "Pokémon Center blocked the request."
                )

                print()
                print(
                    "Close this program with Ctrl+C."
                )

                break


            # Normal successful page
            if result is not None:

                blocked_alert_sent = False

                current_state = {}

                for product in result:

                    url = product["url"]

                    available = product["available"]

                    current_state[url] = available

                    old_state = previous_state.get(
                        url
                    )


                    # Product changed from SOLD OUT
                    # to available
                    if (
                        old_state is False
                        and available is True
                    ):

                        message = (
                            "🚨 POKÉMON CENTER CANADA 🚨\n\n"
                            "🟢 RESTOCK DETECTED!\n\n"
                            f"📦 {product['name']}\n\n"
                            f"🔗 {product['url']}"
                        )

                        print()
                        print(message)
                        print()

                        send_telegram(
                            message
                        )


                previous_state = current_state

                print(
                    f"Monitoring "
                    f"{len(current_state)} "
                    f"ETB/Booster Bundle products."
                )


            print()
            print(
                f"Next check in "
                f"{CHECK_INTERVAL // 60} minutes..."
            )

            print()

            time.sleep(
                CHECK_INTERVAL
            )


if __name__ == "__main__":
    main()