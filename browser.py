from playwright.sync_api import sync_playwright


def open_browser():
    playwright = sync_playwright().start()

    browser = playwright.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto("https://www.w3schools.com/html/")

    return playwright, browser, page


if __name__ == "__main__":
    playwright, browser, page = open_browser()

    input("Press Enter to close...")

    browser.close()
    playwright.stop()
