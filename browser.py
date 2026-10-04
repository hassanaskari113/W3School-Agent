from playwright.sync_api import sync_playwright


def open_exercise(url):
    playwright = sync_playwright().start()

    browser = playwright.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto(url)

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


if __name__ == "__main__":
    url = "https://www.w3schools.com/html/html_exercises.asp"

    playwright, browser, page = open_exercise(url)

    links = get_exercise_links(page)

    for link in links:
        print(link)

    input("Press Enter to close...")

    browser.close()
    playwright.stop()
