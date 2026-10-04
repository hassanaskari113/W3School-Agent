import json
import re
from pathlib import Path

from browser import W3SchoolsBrowser
from config import (
    CATEGORIES,
    MAX_AI_RETRIES,
    PROGRESS_FILE,
    SCREENSHOT_DIR,
)
from document import create_document
from solver import solve_exercise


def load_progress():
    if not PROGRESS_FILE.exists():
        return {"completed": []}

    try:
        return json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))

    except Exception:
        return {"completed": []}


def save_progress(data):
    PROGRESS_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def clean_filename(text):
    text = re.sub(r'[<>:"/\\|?*]', "_", text)

    text = re.sub(r"\s+", "_", text)

    return text[:100]


def already_completed(
    progress,
    subject,
    category,
    question,
):
    for item in progress["completed"]:
        if (
            item["subject"] == subject
            and item["category"] == category
            and item["question"] == question
        ):
            return True

    return False


def solve_category(
    browser,
    subject,
    category,
    url,
    progress,
):
    print()
    print("=" * 70)
    print(f"{subject}: {category}")
    print("=" * 70)

    browser.open(url)

    question_number = 1

    while True:
        print()
        print(f"[{subject}] {category} Question {question_number}")

        exercise = browser.extract_exercise()

        print("Type:", exercise["type"])

        print("Question:", exercise["question"][:300])

        if exercise["type"] == "unknown":
            print("Unknown exercise structure.")
            print("Stopping this category safely.")
            return False

        if exercise["type"] == "drag_drop":
            print("Drag-and-drop detected.")
            print("This category requires the drag/drop handler.")
            return False

        if already_completed(
            progress,
            subject,
            category,
            question_number,
        ):
            print("Already completed. Moving to next.")

            if not browser.next_question():
                return True

            question_number += 1
            continue

        success = False

        for attempt in range(MAX_AI_RETRIES):
            print(f"AI attempt {attempt + 1}/{MAX_AI_RETRIES}")

            result = solve_exercise(exercise)

            print("AI result:", result)

            try:
                browser.submit(result)

            except Exception as error:
                print("Submission error:", error)
                continue

            browser.page.wait_for_timeout(700)

            state = browser.result_state()

            print("Page result:", state)

            if state == "correct":
                success = True
                break

            if state == "wrong":
                print("Wrong answer.")

                try:
                    browser.page.get_by_text("Try Again", exact=True).click()
                except Exception:
                    pass

                browser.page.wait_for_timeout(400)

        if not success:
            print("AI could not solve this exercise.")

            print("Using W3Schools Show Answer as a final recovery mechanism.")

            if browser.show_answer():
                print("Correct answer revealed.")

                # Do NOT record a screenshot as a
                # successful AI solution here.
                #
                # The exercise must actually be
                # submitted after revealing the answer.
                #
                # We stop rather than silently
                # pretending the AI solved it.

            return False

        filename = f"{subject}_{clean_filename(category)}_{question_number:02d}.png"

        screenshot_path = SCREENSHOT_DIR / filename

        browser.screenshot(screenshot_path)

        progress["completed"].append(
            {
                "subject": subject,
                "category": category,
                "question": question_number,
                "type": exercise["type"],
                "screenshot": str(screenshot_path),
            }
        )

        save_progress(progress)

        print("Completed and screenshot saved.")

        if not browser.next_question():
            print("Category completed.")
            return True

        question_number += 1


def main():

    progress = load_progress()

    browser = W3SchoolsBrowser()

    browser.start()

    try:
        for subject, overview_url in CATEGORIES.items():
            print()
            print("#" * 70)
            print(f"DISCOVERING {subject} EXERCISES")
            print("#" * 70)

            browser.open(overview_url)

            categories = browser.discover_categories()

            print(f"Found {len(categories)} {subject} categories.")

            for category in categories:
                solve_category(
                    browser,
                    subject,
                    category["name"],
                    category["url"],
                    progress,
                )

        print()
        print("Creating Word document...")

        create_document(PROGRESS_FILE, "output/W3Schools_Exercises.docx")

        print("Done.")

    finally:
        browser.close()


if __name__ == "__main__":
    main()
