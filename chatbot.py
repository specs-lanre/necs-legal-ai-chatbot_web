from gemini_manager import GeminiManager


class ChatBot:
    """
    Sends a completed prompt to the Gemini chat model
    and returns the generated response.

    This component does NOT:
    - perform retrieval
    - create embeddings
    - build prompts
    - modify knowledge
    """

    def __init__(self):
        print("Initializing ChatBot...")

        self.manager = GeminiManager()

        self.client = self.manager.client
        self.chat_model = self.manager.get_chat_model()

        print(f"Chat model: {self.chat_model}")
        print("ChatBot initialized.")

    def generate_response(self, prompt):
        """
        Send the completed prompt to Gemini
        and return the generated text.
        """

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        print("Sending prompt to Gemini...")

        response = self.client.interactions.create(
            model=self.chat_model,
            input=prompt,
            store=False
        )

        answer = response.output_text

        if not answer:
            raise ValueError("Gemini returned an empty response.")

        print("Response received from Gemini.")

        return answer


if __name__ == "__main__":

    chatbot = ChatBot()

    test_prompt = """
You are Lex, the AI Legal Assistant for NECS Legal.

Answer the following question using the information provided.

Knowledge:
NECS Legal provides Intellectual Property services including
Trademarks, Patents, Industrial Designs, Anti-Counterfeiting,
IP Litigation, Domain Names, Commercial IP, and Strategic IP Advisory.

Question:
What intellectual property services does NECS Legal provide?

Answer professionally and concisely.
"""

    answer = chatbot.generate_response(test_prompt)

    print()
    print("=" * 70)
    print("GEMINI RESPONSE")
    print("=" * 70)
    print(answer)
    print()
    print("=" * 70)
    print("CHATBOT TEST COMPLETE")
    print("=" * 70)
