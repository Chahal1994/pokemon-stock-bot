import requests

URLS = [
    "https://www.pokemoncenter.com/en-ca/search/elite-trainer-box",
    "https://www.pokemoncenter.com/en-ca/search/booster-bundle",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def main():

    print("==========================================")
    print(" Pokémon Center Canada HTTP Test")
    print(" ETBs + Booster Bundles")
    print("==========================================")
    print()

    for url in URLS:

        print("Checking:")
        print(url)
        print()

        try:

            response = requests.get(
                url,
                headers=HEADERS,
                timeout=30,
            )

            print("HTTP status:", response.status_code)
            print("Final URL:", response.url)
            print("Response length:", len(response.text))
            print()

            print("First 3000 characters:")
            print(response.text[:3000])
            print()
            print("------------------------------------------")
            print()

        except Exception as error:

            print("ERROR:")
            print(error)


if __name__ == "__main__":
    main()
