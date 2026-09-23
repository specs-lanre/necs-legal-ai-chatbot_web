
import requests


class ChatClient:
    """
    Reusable client for communicating with the NECS Legal FastAPI service.
    """

    def __init__(
        self,
        api_url="http://127.0.0.1:8000/chat",
        timeout=60,
    ):
        self.api_url = api_url
        self.timeout = timeout

    def ask(self, question):
        """
        Send a question to the FastAPI /chat endpoint
        and return the JSON response.
        """

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        response = requests.post(
            self.api_url,
            json={"question": question},
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()


def ask_lex(question):
    """
    Convenience function for sending a question to Lex.
    """

    client = ChatClient()

    return client.ask(question)

