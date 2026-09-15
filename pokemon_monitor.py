from playwright.sync_api import sync_playwright

URL = "https://www.pokemoncenter.com/en-ca/category/tcg-cards"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)

    page = browser.new_page(
        viewport={"width": 1366, "height": 768},
        locale="en-CA",
    )

    print("Opening Pokémon Center...")
    page.goto(URL, wait_until="domcontentloaded", timeout=60000)

    page.wait_for_timeout(10000)

    print("Final URL:", page.url)
    print("Page title:", page.title())
    print("Page text length:", len(page.locator("body").inner_text()))
    print()
    print(page.locator("body").inner_text()[:5000])

    browser.close()
