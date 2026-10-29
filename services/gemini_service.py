from google import genai
from google.genai import errors
from config import GEMINI_API_KEY, GEMINI_MODEL
from services.knowledge_service import load_knowledge

import time


# ---------------------------------------------------------
# Gemini client
# ---------------------------------------------------------

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ---------------------------------------------------------
# Models to try if the primary model is temporarily
# unavailable.
# ---------------------------------------------------------

FALLBACK_MODELS = [
    GEMINI_MODEL,
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
]


# ---------------------------------------------------------
# Main Gemini function
# ---------------------------------------------------------

def ask_gemini(message: str) -> str:

    # Total timer for the entire function
    total_start = time.perf_counter()

    print("\n" + "=" * 70)
    print("GEMINI REQUEST START")
    print("=" * 70)

    print(f"Visitor message: {message}")

    try:

        # -------------------------------------------------
        # 1. LOAD KNOWLEDGE
        # -------------------------------------------------

        knowledge_start = time.perf_counter()

        knowledge = load_knowledge()

        knowledge_time = time.perf_counter() - knowledge_start

        print("\n[1] KNOWLEDGE LOADING")
        print(f"    Time: {knowledge_time:.4f} seconds")
        print(f"    Knowledge characters: {len(knowledge):,}")

        # -------------------------------------------------
        # 2. BUILD PROMPT
        # -------------------------------------------------

        prompt_start = time.perf_counter()

        prompt = f"""
{knowledge}

Visitor Question:
{message}

Answer as NECS Legal.
"""

        prompt_time = time.perf_counter() - prompt_start

        print("\n[2] PROMPT CONSTRUCTION")
        print(f"    Time: {prompt_time:.4f} seconds")
        print(f"    Prompt characters: {len(prompt):,}")

        # -------------------------------------------------
        # 3. GEMINI MODEL LOOP
        # -------------------------------------------------

        print("\n[3] GEMINI MODEL PROCESSING")

        for model_number, model in enumerate(FALLBACK_MODELS, start=1):

            print("\n" + "-" * 60)
            print(f"MODEL {model_number}/{len(FALLBACK_MODELS)}")
            print(f"Model: {model}")
            print("-" * 60)

            # -------------------------------------------------
            # Retry loop
            # -------------------------------------------------

            for attempt in range(3):

                attempt_number = attempt + 1

                print(
                    f"\nAttempt {attempt_number}/3 "
                    f"for model: {model}"
                )

                # ---------------------------------------------
                # Start timer for Gemini API request
                # ---------------------------------------------

                api_start = time.perf_counter()

                try:

                    response = client.models.generate_content(
                        model=model,
                        contents=prompt
                    )

                    api_time = time.perf_counter() - api_start

                    print(
                        f"Gemini API response time: "
                        f"{api_time:.4f} seconds"
                    )

                    # -----------------------------------------
                    # Check response
                    # -----------------------------------------

                    if response.text:

                        total_time = (
                            time.perf_counter() - total_start
                        )

                        print("\n" + "=" * 70)
                        print("GEMINI REQUEST SUCCESS")
                        print("=" * 70)

                        print(f"Successful model: {model}")
                        print(f"Successful attempt: {attempt_number}")

                        print("\nTIMING SUMMARY")
                        print("-" * 50)

                        print(
                            f"Knowledge loading:     "
                            f"{knowledge_time:.4f} s"
                        )

                        print(
                            f"Prompt construction:   "
                            f"{prompt_time:.4f} s"
                        )

                        print(
                            f"Gemini API call:       "
                            f"{api_time:.4f} s"
                        )

                        print(
                            f"TOTAL ask_gemini():    "
                            f"{total_time:.4f} s"
                        )

                        print("-" * 50)

                        print(
                            f"Response characters: "
                            f"{len(response.text):,}"
                        )

                        print("=" * 70 + "\n")

                        return response.text

                    else:

                        print(
                            "Gemini returned a response "
                            "without response.text."
                        )

                except errors.APIError as e:

                    api_time = time.perf_counter() - api_start

                    print(
                        f"\nGemini API Error "
                        f"(model={model}, "
                        f"attempt={attempt_number})"
                    )

                    print(f"API call time: {api_time:.4f} seconds")
                    print(f"Error: {e}")

                    error_code = getattr(e, "code", None)

                    print(f"Error code: {error_code}")

                    # -----------------------------------------
                    # Temporary service errors
                    # -----------------------------------------

                    if error_code in (429, 500, 503, 504):

                        if attempt < 2:

                            wait_time = 2 ** attempt

                            print(
                                f"Temporary Gemini error."
                            )

                            print(
                                f"Waiting {wait_time} seconds "
                                f"before retry..."
                            )

                            sleep_start = time.perf_counter()

                            time.sleep(wait_time)

                            sleep_time = (
                                time.perf_counter()
                                - sleep_start
                            )

                            print(
                                f"Actual wait time: "
                                f"{sleep_time:.4f} seconds"
                            )

                            continue

                    # -----------------------------------------
                    # Non-retryable error or retries exhausted
                    # -----------------------------------------

                    print(
                        "Moving to next fallback model..."
                    )

                    break

        # -----------------------------------------------------
        # All models failed
        # -----------------------------------------------------

        total_time = time.perf_counter() - total_start

        print("\n" + "=" * 70)
        print("ALL GEMINI MODELS FAILED")
        print("=" * 70)

        print(
            f"Total ask_gemini() time: "
            f"{total_time:.4f} seconds"
        )

        print("=" * 70 + "\n")

        return (
            "I'm sorry, our AI assistant is temporarily unavailable. "
            "Please try again in a few moments."
        )

    # ---------------------------------------------------------
    # Unexpected error
    # ---------------------------------------------------------

    except Exception as e:

        total_time = time.perf_counter() - total_start

        print("\n" + "=" * 70)
        print("UNEXPECTED GEMINI ERROR")
        print("=" * 70)

        print(f"Error: {e}")

        print(
            f"Total ask_gemini() time: "
            f"{total_time:.4f} seconds"
        )

        print("=" * 70 + "\n")

        return (
            "An unexpected error occurred while processing your request."
        )
