from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SCREENSHOT_DIR = BASE_DIR / "screenshots"
OUTPUT_DIR = BASE_DIR / "output"

PROGRESS_FILE = OUTPUT_DIR / "progress.json"
WORD_FILE = OUTPUT_DIR / "W3Schools_Exercises.docx"


CATEGORIES = {
    "HTML": "https://www.w3schools.com/html/html_exercises.asp",
    # "CSS": "https://www.w3schools.com/css/css_exercises.asp",
    # "JavaScript": "https://www.w3schools.com/js/js_exercises.asp",
}


BROWSER_WIDTH = 1440
BROWSER_HEIGHT = 1000


MAX_AI_RETRIES = 3


SCREENSHOT_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
