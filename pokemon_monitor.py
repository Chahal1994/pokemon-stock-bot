import requests
from bs4 import BeautifulSoup

URL = "https://www.google.com/search?q=site%3Apokemoncenter.com%2Fen-ca+%22Elite+Trainer+Box%22+Pok%C3%A9mon+Center"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def main():

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30,
    )

    print("HTTP status:", response.status_code)

    soup = BeautifulSoup(response.text, "html.parser")

    print()
    print("Google results:")
    print("------------------------------------------")

    found = 0

    for link in soup.select("a"):

        href = link.get("href", "")
        text = link.get_text(" ", strip=True)

        if "pokemoncenter.com" in href:

            print()
            print("TITLE:", text[:300])
            print("URL:", href[:500])

            found += 1

    print()
    print("Pokémon Center links found:", found)


if __name__ == "__main__":
    main()
