import requests

URL = "https://www.pokemoncenter.com/en-ca/product/10-10447-111/pokemon-tcg-30th-celebration-pokemon-center-elite-trainer-box"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers, timeout=30)

print("HTTP status:", response.status_code)
print("Page length:", len(response.text))
print()
print(response.text[:1000])
