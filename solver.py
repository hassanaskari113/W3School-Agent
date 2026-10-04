import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def solve_exercise(question, options):
    prompt = f"""
Solve this W3Schools exercise.

Question:
{question}

Options:
{options}

Return ONLY the number of the correct option.
Example: 0
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    return response.choices[0].message.content.strip()
