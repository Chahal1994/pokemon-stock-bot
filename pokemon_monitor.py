import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


PRODUCTS = [

    # ==============================
    # BOOSTER BUNDLES
    # ==============================

    {
        "name": "Mega Evolution — Pitch Black Booster Bundle",
        "search": '"Pitch Black" "Booster Bundle" site:pokemoncenter.com/en-ca',
    },

    {
        "name": "Mega Evolution — Chaos Rising Booster Bundle",
        "search": '"Chaos Rising" "Booster Bundle" site:pokemoncenter.com/en-ca',
    },

    {
        "name": "Mega Evolution — Perfect Order Booster Bundle",
        "search": '"Perfect Order" "Booster Bundle" site:pokemoncenter.com/en-ca',
    },

    {
        "name": "Mega Evolution — Ascended Heroes Booster Bundle",
        "search": '"Ascended Heroes" "Booster Bundle" site:pokemoncenter.com/en-ca',
    },


    # ==============================
    # ELITE TRAINER BOXES
    # ==============================

    {
        "name": "30th Celebration Pokémon Center Elite Trainer Box",
        "search": '"30th Celebration" "Pokémon Center Elite Trainer Box" site:pokemoncenter.com/en-ca',
    },

    {
        "name": "Mega Evolution — Pitch Black Pokémon Center Elite Trainer Box",
        "search": '"Pitch Black" "Pokémon Center Elite Trainer Box" site:pokemoncenter.com/en-ca',
    },

    {
        "name": "Mega Evolution — Chaos Rising Pokémon Center Elite Trainer Box",
        "search": '"Chaos Rising" "Pokémon Center Elite Trainer Box" site:pokemoncenter.com/en-ca',
    },

    {
        "name": "Mega Evolution — Perfect Order Pokémon Center Elite Trainer Box",
        "search": '"Perfect Order" "Pokémon Center Elite Trainer Box" site:pokemoncenter.com/en-ca',
    },

    {
        "name": "Mega Evolution — Ascended Heroes Pokémon Center Elite Trainer Box",
        "search": '"Ascended Heroes" "Pokémon Center Elite Trainer Box" site:pokemoncenter.com/en-ca',
    },


    # ==============================
    # 30TH CELEBRATION
    # ==============================

    {
        "name": "30th Celebration Booster Bundle",
        "search": '"30th Celebration" "Booster Bundle" site:pokemoncenter.com/en-ca',
    },

    {
        "name": "30th Celebration Booster Pack",
        "search": '"30th Celebration" "Booster Pack" site:pokemoncenter.com/en-ca',
    },

    {
        "name": "30th Celebration Mega Booster",
        "search": '"30th Celebration" "Mega Booster" site:pokemoncenter.com/en-ca',
    },

    {
        "name": "30th Celebration Futuristic Box",
        "search": '"30th Celebration" "Futuristic Box" site:pokemoncenter.com/en-ca',
    },

    {
        "name": "30th Celebration Partner Set",
        "search": '"30th Celebration" "Partner Set" site:pokemoncenter.com/en-ca',
    },


    # ==============================
    # BOOSTER PACKS
    # ==============================

    {
        "name": "Mega Evolution Booster Pack",
        "search": '"Mega Evolution" "Booster Pack" site:pokemoncenter.com/en-ca',
    },

    {
        "name": "Mega Evolution — Pitch Black Booster Pack",
        "search": '"Pitch Black" "Booster Pack" site:pokemoncenter.com/en-ca',
    },

    {
        "name": "Mega Evolution — Chaos Rising Booster Pack",
        "search": '"Chaos Rising" "Booster Pack" site:pokemoncenter.com/en-ca',
    },

    {
        "name": "Mega Evolution — Perfect Order Booster Pack",
        "search": '"Perfect Order" "Booster Pack" site:pokemoncenter.com/en-ca',
    },

    {
        "name": "Mega Evolution — Ascended Heroes Booster Pack",
        "search": '"Ascended Heroes" "Booster Pack" site:pokemoncenter.com/en-ca',
    },

]


def send_telegram(message):

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials are missing.")
        return

    url = (
        f"https://api.telegram.org/bot"
        f"{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

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


def check_product(product):

    search_url = (
        "https://www.google.com/search?q="
        + quote_plus(product["search"])
    )

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        search_url,
        headers=headers,
        timeout=30,
    )

    print()
    print("==========================================")
    print(product["name"])
    print("Google HTTP status:", response.status_code)
    print("==========================================")

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    found_links = []

    for link in soup.select("a"):

        href = link.get("href", "")
        text = link.get_text(" ", strip=True)

        if "pokemoncenter.com/en-ca" in href:

            found_links.append(
                {
                    "text": text,
                    "url": href,
                }
            )

    if not found_links:

        print("No Pokémon Center result found.")
        return

    print("Pokémon Center result found!")

    for result in found_links[:3]:

        print()
        print("Title:", result["text"][:300])
        print("URL:", result["url"][:500])


def main():

    print("==========================================")
    print(" Pokémon Center Canada Stock Monitor")
    print("==========================================")
    print()
    print("Products being monitored:", len(PRODUCTS))
    print()

    for product in PRODUCTS:

        try:

            check_product(product)

        except Exception as error:

            print()
            print("ERROR checking:")
            print(product["name"])
            print(error)

    print()
    print("==========================================")
    print("Monitoring test complete.")
    print("==========================================")


if __name__ == "__main__":
    main()
