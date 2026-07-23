
from services.gemini_service import ask_gemini


def process_chat(message: str) -> str:
    """
    Main chatbot service.

    Later this function will:
        • Save chat history
        • Query PostgreSQL
        • Search knowledge base
        • Call Gemini
        • Log conversations

    For now it simply calls Gemini.
    """

    reply = ask_gemini(message)

    return reply
