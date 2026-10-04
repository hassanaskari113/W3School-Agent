from playwright.sync_api import sync_playwright

from solver import solve_exercise


def open_exercise(url):
    playwright = sync_playwright().start()

    browser = playwright.chromium.launch(headless=False)

    page = browser.new_page()

    page.goto(url, wait_until="domcontentloaded", timeout=60000)

    return playwright, browser, page


def get_question_and_options(page):
    question = page.locator("h2").first.inner_text().strip()

    options = page.locator("input[type='radio']").evaluate_all("""
        elements => elements.map(e => e.parentElement.innerText.trim())
    """)

    return question, options


def submit_answer(page, answer_index):
    page.locator("input[type='radio']").nth(answer_index).check()
    page.get_by_text("Submit Answer »").click()


def is_correct(page):
    return page.get_by_text("Correct Answer!").count() > 0


def go_to_next_question(page):
    page.get_by_text("Next Question »").click()
    page.wait_for_timeout(500)


if __name__ == "__main__":
    url = "https://www.w3schools.com/html/exercise.asp?x=xrcise_attributes1"

    playwright, browser, page = open_exercise(url)

    question, options = get_question_and_options(page)

    answer = solve_exercise(question, options)

    print("AI Answer:", answer)

    submit_answer(page, int(answer))

    page.wait_for_timeout(1000)

    if is_correct(page):
        print("AI solved it correctly!")
        go_to_next_question(page)
        print("Moved to next question!")
    else:
        print("AI answer was wrong!")

    input("\nPress Enter to close...")

    browser.close()
    playwright.stop()
