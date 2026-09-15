import requests

URL = "https://www.google.com/search?q=site%3Apokemoncenter.com%2Fen-ca+%22Elite+Trainer+Box%22+Pok%C3%A9mon+Center"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def main():

    print("==========================================")
    print(" Pokémon Center Canada Search Test")
    print("==========================================")
    print()

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30,
    )

    print("HTTP status:", response.status_code)
    print("Response length:", len(response.text))
    print()
    print("First 5000 characters:")
    print(response.text[:5000])


if __name__ == "__main__":
    main()
