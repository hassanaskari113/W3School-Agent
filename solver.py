import json
import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError("GROQ_API_KEY is missing from .env")


client = Groq(api_key=api_key)

MODEL = "openai/gpt-oss-120b"


def solve_exercise(exercise):
    prompt = f"""
You are an expert web development tutor solving a W3Schools exercise.

Your job is to determine the EXACT answer required by the exercise.

IMPORTANT RULES:

1. Carefully understand the question.
2. Never invent an answer.
3. For multiple choice, return the exact option index.
4. For fill-in-the-blank, return one answer for every blank, in order.
5. Preserve exact syntax where code is required.
6. Do not confuse example values with blanks.
7. If the exercise contains HTML, CSS, or JavaScript, reason about valid syntax.
8. The answer must directly solve THIS exercise.
9. Return JSON only.
10. Do not explain your reasoning.

EXERCISE:

{json.dumps(exercise, indent=2, ensure_ascii=False)}

Return exactly one of these formats:

Multiple choice:
{{
    "type": "multiple_choice",
    "answer": 0
}}

Fill in blanks:
{{
    "type": "fill_blank",
    "answers": ["answer1", "answer2"]
}}

Code:
{{
    "type": "code",
    "answers": ["complete code"]
}}

Drag and drop:
{{
    "type": "drag_drop",
    "answers": ["item1", "item2"]
}}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
    )

    content = response.choices[0].message.content.strip()

    if content.startswith("```"):
        content = content.replace("```json", "", 1)

        if content.endswith("```"):
            content = content[:-3]

        content = content.strip()

    try:
        result = json.loads(content)
    except json.JSONDecodeError as error:
        raise RuntimeError(f"Groq returned invalid JSON:\n{content}") from error

    return result
