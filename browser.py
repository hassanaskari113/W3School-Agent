from playwright.sync_api import sync_playwright


def open_exercise(url):
    playwright = sync_playwright().start()

    browser = playwright.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto(url, wait_until="domcontentloaded", timeout=60000)

    return playwright, browser, page


def get_exercise_text(page):
    text = page.locator("body").inner_text()
    return text


def get_exercise_links(page):
    links = page.locator("a").evaluate_all("""
        elements => elements
            .map(a => ({
                text: a.innerText.trim(),
                href: a.href
            }))
            .filter(x => x.text.includes("exercises"))
    """)

    return links


def inspect_exercise(page):
    print("\n--- EXERCISE PAGE ---")
    print(page.locator("body").inner_text())


if __name__ == "__main__":
    url = "https://www.w3schools.com/html/exercise.asp?x=xrcise_attributes1"

    playwright, browser, page = open_exercise(url)

    inspect_exercise(page)

    input("\nPress Enter to close...")

    browser.close()
    playwright.stop()
