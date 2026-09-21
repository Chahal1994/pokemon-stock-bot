import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re


# ============================================================
# SETTINGS
# ============================================================

BASE_URL = "https://celadoninfo.com/ca"
RELEASES_URL = f"{BASE_URL}/releases"

STATE_FILE = "stock_state.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/140.0.0.0 Safari/537.36"
    )
}


# ============================================================
# TELEGRAM CONFIG
# ============================================================

# The script first looks for environment variables.
# If they don't exist, it tries to read them from config.py.

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


try:
    import config

    if not TELEGRAM_BOT_TOKEN:
        TELEGRAM_BOT_TOKEN = getattr(
            config,
            "TELEGRAM_BOT_TOKEN",
            getattr(config, "BOT_TOKEN", None)
        )

    if not TELEGRAM_CHAT_ID:
        TELEGRAM_CHAT_ID = getattr(
            config,
            "TELEGRAM_CHAT_ID",
            getattr(config, "CHAT_ID", None)
        )

except ImportError:
    pass


# ============================================================
# HTTP
# ============================================================

def get_page(url):

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.text


# ============================================================
# FIND PRODUCTS
# ============================================================

def find_products():

    print("Loading Celadon Canada releases...")

    html = get_page(RELEASES_URL)

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    products = []

    for link in soup.find_all("a", href=True):

        name = link.get_text(
            " ",
            strip=True
        )

        href = link["href"]

        if not name:
            continue

        name_lower = name.lower()

        # Only monitor:
        # - Booster Bundles
        # - Elite Trainer Boxes

        if (
            "booster bundle" not in name_lower
            and "elite trainer box" not in name_lower
        ):
            continue

        url = urljoin(
            BASE_URL,
            href
        )

        # Avoid duplicate products

        if any(
            product["url"] == url
            for product in products
        ):
            continue

        products.append({
            "name": name,
            "url": url
        })

    return products


# ============================================================
# GET PRODUCT DETAILS
# ============================================================

def get_product_details(product):

    html = get_page(
        product["url"]
    )

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    page_text = soup.get_text(
        "\n",
        strip=True
    )

    # --------------------------------------------------------
    # PRODUCT NAME
    # --------------------------------------------------------

    title = soup.find("h1")

    if title:

        product_name = title.get_text(
            " ",
            strip=True
        )

    else:

        product_name = product["name"]


    # --------------------------------------------------------
    # MSRP
    # --------------------------------------------------------

    msrp = "TBA"

    msrp_match = re.search(
        r"MSRP:\s*\$([\d,]+\.\d{2})\s*CAD",
        page_text
    )

    if msrp_match:

        msrp = (
            f"${msrp_match.group(1)} CAD"
        )


    # --------------------------------------------------------
    # RETAILERS
    # --------------------------------------------------------

    retailers = []

    for link in soup.find_all(
        "a",
        href=True
    ):

        if link.get_text(
            " ",
            strip=True
        ) != "View Product":

            continue


        # The retailer container is two levels above
        container = link.parent.parent

        if not container:
            continue


        # ----------------------------------------------------
        # RETAILER NAME
        # ----------------------------------------------------

        retailer = "Unknown Retailer"

        retailer_name_tag = container.select_one(
            "a.group p.font-semibold"
        )

        if retailer_name_tag:

            retailer = retailer_name_tag.get_text(
                " ",
                strip=True
            )


        # ----------------------------------------------------
        # PRICE
        # ----------------------------------------------------

        price = "TBA"

        price_tag = container.select_one(
            "div.text-right p.font-semibold"
        )

        if price_tag:

            price_text = price_tag.get_text(
                " ",
                strip=True
            )

            price_match = re.search(
                r"\$[\d,]+\.\d{2}\s*CAD",
                price_text
            )

            if price_match:

                price = price_match.group(0)


        # ----------------------------------------------------
        # STOCK STATUS
        # ----------------------------------------------------

        status = "Unknown"

        container_text = container.get_text(
            " ",
            strip=True
        )

        if "In Stock" in container_text:

            status = "In Stock"

        elif "Out of Stock" in container_text:

            status = "Out of Stock"

        elif "Unknown" in container_text:

            status = "Unknown"


        # ----------------------------------------------------
        # DIRECT PRODUCT URL
        # ----------------------------------------------------

        retailer_url = link.get(
            "href"
        )

        if not retailer_url:

            continue


        retailers.append({
            "retailer": retailer,
            "price": price,
            "status": status,
            "url": retailer_url
        })


    # --------------------------------------------------------
    # REMOVE DUPLICATE RETAILERS
    # --------------------------------------------------------

    unique_retailers = {}

    for retailer in retailers:

        key = (
            retailer["retailer"].strip().lower()
            + "|"
            + retailer["status"].strip().lower()
            + "|"
            + retailer["url"].strip().lower()
        )

        if key not in unique_retailers:

            unique_retailers[key] = retailer


    retailers = list(
        unique_retailers.values()
    )


    return {
        "name": product_name,
        "celadon_url": product["url"],
        "msrp": msrp,
        "retailers": retailers
    }


# ============================================================
# STATE FILE
# ============================================================

def load_state():

    if not os.path.exists(
        STATE_FILE
    ):

        return {}


    try:

        with open(
            STATE_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return {}


def save_state(state):

    with open(
        STATE_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            state,
            file,
            indent=2,
            ensure_ascii=False
        )


# ============================================================
# SEND TELEGRAM
# ============================================================

def send_telegram(message):

    if not TELEGRAM_BOT_TOKEN:

        print(
            "WARNING: TELEGRAM_BOT_TOKEN not found."
        )

        return False


    if not TELEGRAM_CHAT_ID:

        print(
            "WARNING: TELEGRAM_CHAT_ID not found."
        )

        return False


    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )


    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "disable_web_page_preview": False
    }


    try:

        response = requests.post(
            url,
            data=payload,
            timeout=30
        )

        response.raise_for_status()

        print(
            "Telegram alert sent."
        )

        return True

    except Exception as error:

        print(
            f"Telegram error: {error}"
        )

        return False


# ============================================================
# CREATE TELEGRAM MESSAGE
# ============================================================

def create_alert(product, retailer):

    message = (
        "🚨 Pokémon Stock Alert 🚨\n\n"
        f"🎴 {product['name']}\n\n"
        f"🏪 Retailer: {retailer['retailer']}\n"
        f"💰 Price: {retailer['price']}\n"
        f"📦 Status: {retailer['status']}\n"
        f"🏷️ MSRP: {product['msrp']}\n\n"
        f"🛒 Buy:\n{retailer['url']}\n\n"
        f"🔎 Celadon:\n{product['celadon_url']}"
    )

    return message


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)

    print(
        "Pokémon Stock Monitor - Celadon Canada"
    )

    print(
        "ETBs + Booster Bundles"
    )

    print("=" * 70)


    # --------------------------------------------------------
    # LOAD PREVIOUS STATE
    # --------------------------------------------------------

    previous_state = load_state()

    first_run = (
        len(previous_state) == 0
    )


    # --------------------------------------------------------
    # FIND PRODUCTS
    # --------------------------------------------------------

    products = find_products()

    print(
        f"\nFound {len(products)} matching products."
    )


    current_state = {}

    alerts = []


    # --------------------------------------------------------
    # CHECK EACH PRODUCT
    # --------------------------------------------------------

    for index, product in enumerate(
        products,
        start=1
    ):

        print(
            f"\n[{index}/{len(products)}] "
            f"Checking {product['name']}..."
        )


        try:

            details = get_product_details(
                product
            )

        except Exception as error:

            print(
                f"ERROR checking product: {error}"
            )

            continue


        product_name = details["name"]


        # ----------------------------------------------------
        # CHECK RETAILERS
        # ----------------------------------------------------

        for retailer in details["retailers"]:

            retailer_name = retailer["retailer"]

            status = retailer["status"]

            url = retailer["url"]


            # Unique state key

            state_key = (
                f"{product_name}|"
                f"{retailer_name}|"
                f"{url}"
            )


            current_state[state_key] = {
                "status": status,
                "price": retailer["price"],
                "product": product_name,
                "retailer": retailer_name,
                "url": url
            }


            # ------------------------------------------------
            # ONLY CARE ABOUT IN STOCK
            # ------------------------------------------------

            if status != "In Stock":

                continue


            previous = previous_state.get(
                state_key
            )


            # ------------------------------------------------
            # FIRST RUN
            # ------------------------------------------------

            if first_run:

                # Establish baseline.
                # Don't send dozens of alerts immediately.

                continue


            # ------------------------------------------------
            # STOCK CHANGE
            # ------------------------------------------------

            previous_status = (
                previous.get("status")
                if previous
                else "Unknown"
            )


            if previous_status != "In Stock":

                alerts.append({
                    "product": details,
                    "retailer": retailer
                })


    # --------------------------------------------------------
    # SAVE CURRENT STATE
    # --------------------------------------------------------

    save_state(
        current_state
    )


    # --------------------------------------------------------
    # SEND ALERTS
    # --------------------------------------------------------

    if first_run:

        print(
            "\nFirst run detected."
        )

        print(
            "Stock baseline saved."
        )

        print(
            "No Telegram alerts sent."
        )

        return


    if not alerts:

        print(
            "\nNo new stock detected."
        )

        return


    print(
        f"\nFound {len(alerts)} new "
        f"stock alert(s)."
    )


    for alert in alerts:

        product = alert["product"]

        retailer = alert["retailer"]


        print(
            "\n" + "-" * 70
        )

        print(
            f"NEW STOCK: {product['name']}"
        )

        print(
            f"Retailer: {retailer['retailer']}"
        )

        print(
            f"Price: {retailer['price']}"
        )

        print(
            f"URL: {retailer['url']}"
        )


        message = create_alert(
            product,
            retailer
        )


        send_telegram(
            message
        )


    print(
        "\nMonitor finished."
    )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()