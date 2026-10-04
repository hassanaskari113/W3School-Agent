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


if __name__ == "__main__":
    url = input("Enter exercise URL: ")

    playwright, browser, page = open_exercise(url)

    exercise_text = get_exercise_text(page)

    print("\n--- PAGE CONTENT ---\n")
    print(exercise_text)

    input("\nPress Enter to close...")

    browser.close()
    playwright.stop()
