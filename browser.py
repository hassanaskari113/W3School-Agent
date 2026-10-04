from playwright.sync_api import sync_playwright


def open_exercise(url):
    playwright = sync_playwright().start()

    browser = playwright.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto(url)

    return playwright, browser, page


if __name__ == "__main__":
    url = input("Enter exercise URL: ")

    playwright, browser, page = open_exercise(url)

    input("Press Enter to close...")

    browser.close()
    playwright.stop()
