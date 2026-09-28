from google import genai
from google.genai import errors
from config import GEMINI_API_KEY, GEMINI_MODEL
from services.knowledge_service import load_knowledge

import time


client = genai.Client(
    api_key=GEMINI_API_KEY
)


# Models to try if the primary model is temporarily unavailable.
FALLBACK_MODELS = [
    GEMINI_MODEL,
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
]


def ask_gemini(message: str) -> str:

    try:

        knowledge = load_knowledge()

        prompt = f"""
{knowledge}

Visitor Question:
{message}

Answer as NECS Legal.
"""

        for model in FALLBACK_MODELS:

            print(f"Trying Gemini model: {model}")

            for attempt in range(3):

                try:

                    response = client.models.generate_content(
                        model=model,
                        contents=prompt
                    )

                    if response.text:
                        print(f"Gemini model succeeded: {model}")
                        return response.text

                except errors.APIError as e:

                    print(
                        f"Gemini API Error "
                        f"(model={model}, attempt={attempt + 1}): {e}"
                    )

                    # Retry temporary server/service errors.
                    if getattr(e, "code", None) in (429, 500, 503, 504):

                        if attempt < 2:
                            wait_time = 2 ** attempt

                            print(
                                f"Retrying in {wait_time} seconds..."
                            )

                            time.sleep(wait_time)
                            continue

                    break

        return (
            "I'm sorry, our AI assistant is temporarily unavailable. "
            "Please try again in a few moments."
        )

    except Exception as e:

        print(f"Unexpected Error: {e}")

        return (
            "An unexpected error occurred while processing your request."
        )
