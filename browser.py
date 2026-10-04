import re
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright


class W3SchoolsBrowser:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    def start(self):
        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(headless=False)

        self.page = self.browser.new_page(
            viewport={
                "width": 1440,
                "height": 1000,
            }
        )

    def close(self):
        if self.browser:
            self.browser.close()

        if self.playwright:
            self.playwright.stop()

    def open(self, url):
        self.page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        self.page.wait_for_timeout(1000)

        self.reset_completed_exercise()

    def reset_completed_exercise(self):
        """
        W3Schools may remember completed exercises.
        If the page opens in the completed state,
        click Yes to take the exercise again.
        """

        yes_button = self.page.get_by_text("Yes", exact=True)

        if yes_button.count() > 0:
            visible_yes = False

            for i in range(yes_button.count()):
                try:
                    if yes_button.nth(i).is_visible():
                        visible_yes = True
                        yes_button.nth(i).click()
                        self.page.wait_for_timeout(700)
                        break
                except Exception:
                    pass

            if visible_yes:
                return

    @staticmethod
    def clean(text):
        return re.sub(r"\s+", " ", text or "").strip()

    def title(self):
        headings = self.page.locator("h1, h2, h3")

        for i in range(headings.count()):
            text = self.clean(headings.nth(i).inner_text())

            if text.startswith("Exercise:"):
                return text.replace("Exercise:", "", 1).strip()

        return "Unknown"

    def discover_categories(self):
        """
        Get actual exercise category URLs
        from the W3Schools exercise page.
        """

        links = self.page.locator("a")

        categories = []

        for i in range(links.count()):
            link = links.nth(i)

            try:
                text = self.clean(link.inner_text())

                href = link.get_attribute("href")

                if not href:
                    continue

                if "exercise.asp?x=" not in href:
                    continue

                if not text:
                    continue

                full_url = link.evaluate("el => el.href")

                categories.append(
                    {
                        "name": text,
                        "url": full_url,
                    }
                )

            except Exception:
                continue

        unique = []
        seen = set()

        for item in categories:
            if item["url"] in seen:
                continue

            seen.add(item["url"])
            unique.append(item)

        return unique

    def visible_submit(self):
        buttons = self.page.get_by_text("Submit Answer »", exact=True)

        for i in range(buttons.count()):
            try:
                button = buttons.nth(i)

                if button.is_visible():
                    return button

            except Exception:
                pass

        return None

    def visible_next(self):
        buttons = self.page.get_by_text("Next Question »", exact=True)

        for i in range(buttons.count()):
            try:
                button = buttons.nth(i)

                if button.is_visible():
                    return button

            except Exception:
                pass

        return None

    def result_state(self):
        correct = self.page.get_by_text("Correct Answer!", exact=True)

        for i in range(correct.count()):
            try:
                if correct.nth(i).is_visible():
                    return "correct"
            except Exception:
                pass

        wrong = self.page.get_by_text("Wrong Answer!", exact=True)

        for i in range(wrong.count()):
            try:
                if wrong.nth(i).is_visible():
                    return "wrong"
            except Exception:
                pass

        return "pending"

    def question_container(self):
        """
        Find the section containing the active exercise.

        We use the Submit button as an anchor because
        W3Schools places the question controls around it.
        """

        submit = self.visible_submit()

        if not submit:
            return self.page.locator("body")

        return submit.locator("xpath=ancestor::*[self::div or self::section][1]")

    def exercise_type(self):
        container = self.question_container()

        if container.locator("input[type='radio']").count() > 0:
            return "multiple_choice"

        if container.locator("input.editablesection").count() > 0:
            return "fill_blank"

        if container.locator("textarea").count() > 0:
            return "code"

        if container.locator("[contenteditable='true']").count() > 0:
            return "code"

        if container.locator("[draggable='true']").count() > 0:
            return "drag_drop"

        return "unknown"

    def extract_question_text(self):
        """
        Extract visible exercise text and remove
        obvious control labels.
        """

        container = self.question_container()

        text = self.clean(container.inner_text())

        unwanted = [
            "Show Answer",
            "Hide Answer",
            "Submit Answer »",
            "Try Again",
            "Correct Answer!",
            "Wrong Answer!",
        ]

        for value in unwanted:
            text = text.replace(value, "")

        return self.clean(text)

    def extract_multiple_choice(self):
        container = self.question_container()

        radios = container.locator("input[type='radio']")

        options = []

        for i in range(radios.count()):
            radio = radios.nth(i)

            option_text = radio.evaluate("""
                element => {
                    let node = element;

                    for (let i = 0; i < 5 && node; i++) {
                        const text =
                            node.parentElement?.innerText?.trim();

                        if (text) {
                            return text;
                        }

                        node = node.parentElement;
                    }

                    return "";
                }
            """)

            options.append(self.clean(option_text))

        return {
            "type": "multiple_choice",
            "question": self.extract_question_text(),
            "options": options,
            "fields": [],
        }

    def extract_fill_blank(self):
        container = self.question_container()

        fields = container.locator("input.editablesection")

        field_count = fields.count()

        template = ""

        if field_count > 0:
            field = fields.nth(0)

            template = field.evaluate("""
                element => {
                    let node = element.parentElement;

                    for (let i = 0; i < 8 && node; i++) {
                        if (node.innerText?.trim()) {
                            return node.innerText.trim();
                        }

                        node = node.parentElement;
                    }

                    return "";
                }
            """)

        field_info = []

        for i in range(field_count):
            field = fields.nth(i)

            field_info.append(
                {
                    "index": i,
                    "placeholder": field.get_attribute("placeholder"),
                    "maxlength": field.get_attribute("maxlength"),
                }
            )

        return {
            "type": "fill_blank",
            "question": self.clean(template),
            "options": [],
            "fields": field_info,
        }

    def extract_code(self):
        container = self.question_container()

        fields = []

        textareas = container.locator("textarea")

        for i in range(textareas.count()):
            fields.append(
                {
                    "index": i,
                    "kind": "textarea",
                    "value": textareas.nth(i).input_value(),
                }
            )

        editables = container.locator("[contenteditable='true']")

        for i in range(editables.count()):
            fields.append(
                {
                    "index": i,
                    "kind": "contenteditable",
                    "value": editables.nth(i).inner_text(),
                }
            )

        return {
            "type": "code",
            "question": self.extract_question_text(),
            "options": [],
            "fields": fields,
        }

    def extract_drag_drop(self):
        container = self.question_container()

        items = container.locator("[draggable='true']")

        values = []

        for i in range(items.count()):
            values.append(self.clean(items.nth(i).inner_text()))

        return {
            "type": "drag_drop",
            "question": self.extract_question_text(),
            "options": values,
            "fields": [],
        }

    def extract_exercise(self):
        kind = self.exercise_type()

        if kind == "multiple_choice":
            return self.extract_multiple_choice()

        if kind == "fill_blank":
            return self.extract_fill_blank()

        if kind == "code":
            return self.extract_code()

        if kind == "drag_drop":
            return self.extract_drag_drop()

        return {
            "type": "unknown",
            "question": self.extract_question_text(),
            "options": [],
            "fields": [],
        }

    def submit_multiple_choice(self, answer):
        container = self.question_container()

        radios = container.locator("input[type='radio']")

        index = int(answer)

        if index < 0 or index >= radios.count():
            raise ValueError(f"Invalid option index: {index}")

        radios.nth(index).check()

        button = self.visible_submit()

        if not button:
            raise RuntimeError("Submit button not found.")

        button.click()

    def submit_fill_blank(self, answers):
        container = self.question_container()

        fields = container.locator("input.editablesection")

        if not isinstance(answers, list):
            answers = [answers]

        if len(answers) != fields.count():
            raise ValueError(
                "AI answer count does not match "
                f"the number of blanks. "
                f"Expected {fields.count()}, "
                f"got {len(answers)}."
            )

        for i, answer in enumerate(answers):
            fields.nth(i).fill(str(answer))

        button = self.visible_submit()

        if not button:
            raise RuntimeError("Submit button not found.")

        button.click()

    def submit_code(self, answers):
        if not answers:
            raise ValueError("No code returned by AI.")

        code = str(answers[0])

        container = self.question_container()

        textarea = container.locator("textarea")

        if textarea.count() > 0:
            textarea.first.fill(code)

        else:
            editable = container.locator("[contenteditable='true']")

            if editable.count() == 0:
                raise RuntimeError("No code editor found.")

            editable.first.fill(code)

        button = self.visible_submit()

        if not button:
            raise RuntimeError("Submit button not found.")

        button.click()

    def submit(self, result):
        kind = result.get("type")

        if kind == "multiple_choice":
            self.submit_multiple_choice(result["answer"])

        elif kind == "fill_blank":
            self.submit_fill_blank(result["answers"])

        elif kind == "code":
            self.submit_code(result["answers"])

        else:
            raise RuntimeError(f"Unsupported exercise type: {kind}")

    def show_answer(self):
        button = self.page.get_by_text("Show Answer", exact=True)

        for i in range(button.count()):
            try:
                if button.nth(i).is_visible():
                    button.nth(i).click()
                    self.page.wait_for_timeout(300)
                    return True
            except Exception:
                pass

        return False

    def screenshot(self, path):
        self.page.screenshot(path=str(path), full_page=True)

    def next_question(self):
        button = self.visible_next()

        if not button:
            return False

        button.click()

        self.page.wait_for_timeout(700)

        return True
