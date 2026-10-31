import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=API_KEY)

MODEL = "gemma-4-26b-a4b-it"


def ask_gemma(prompt):
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return response.text