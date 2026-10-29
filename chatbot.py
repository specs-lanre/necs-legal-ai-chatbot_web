
import time

from gemini_manager import GeminiManager


class ChatBot:
    def __init__(self):
        print("Initializing ChatBot...")

        self.manager = GeminiManager()
        self.client = self.manager.client
        self.chat_model = self.manager.get_chat_model()

        print(f"Chat model: {self.chat_model}")
        print("ChatBot initialized.")

    def generate_response(self, prompt):
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        print("Sending prompt to Gemini...")
        start_time = time.perf_counter()

        try:
            response = self.client.interactions.create(
                model=self.chat_model,
                input=prompt,
                store=False,
                generation_config={
                    "thinking_level": "low",
                    "max_output_tokens": 4096,
                },
            )

            elapsed = time.perf_counter() - start_time

            print(
                f"Gemini generation API time: {elapsed:.2f} seconds"
            )

        except Exception as ex:
            elapsed = time.perf_counter() - start_time

            print(
                f"Gemini generation failed after "
                f"{elapsed:.2f} seconds: "
                f"{type(ex).__name__}: {ex}"
            )
            raise

        status = getattr(response, "status", None)
        answer = response.output_text or ""

        print(f"Gemini response status: {status}")
        print(f"Gemini output length: {len(answer)}")
        print(f"Gemini output: {answer!r}")

        if status == "incomplete":
            raise RuntimeError(
                "Gemini returned an incomplete response. "
                "Check the output-token limit and response details."
            )

        if not answer.strip():
            raise ValueError("Gemini returned an empty response.")

        print("Response received from Gemini.")
        return answer


if __name__ == "__main__":
    chatbot = ChatBot()

    test_prompt = """
    You are Sujo, the AI Legal Assistant for NECS Legal.

    Answer the visitor's question directly and concisely.
    Do not return only a greeting.
    Do not guarantee legal outcomes.

    Question:
    Can NECS Legal guarantee that I will win my intellectual
    property lawsuit?
    """

    print(chatbot.generate_response(test_prompt))
