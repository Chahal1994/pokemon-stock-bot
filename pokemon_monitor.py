import requests

URL = "https://www.pokemoncenter.com/en-ca/category/tcg-cards"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/140.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-CA,en;q=0.9",
}

response = requests.get(URL, headers=headers, timeout=30)

print("HTTP status:", response.status_code)
print("Final URL:", response.url)
print("Page length:", len(response.text))
print()
print(response.text[:3000])
