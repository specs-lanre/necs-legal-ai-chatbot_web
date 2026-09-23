from google import genai
from dotenv import load_dotenv
import os
from pathlib import Path
import json

load_dotenv()


class GeminiManager:

    def __init__(self):

        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

        self.PREFERRED_MODELS = [
            "models/gemini-3.6-flash",
            "models/gemini-3.5-flash",
            "models/gemini-3.5-flash-lite",
            "models/gemini-3.1-flash-lite",
            "models/gemini-2.5-flash",
            "models/gemini-2.0-flash",
            "models/gemma-4-26b-a4b-it"
        ]

        self.models_folder = Path("config")
        self.models_folder.mkdir(exist_ok=True)

        self.models_file = self.models_folder / "models.json"

        self.chat_models = []
        self.embedding_models = []

        self.chat_model = None
        self.embedding_model = None

        # Load saved models if available,
        # otherwise discover and save them.
        if not self.load_models():
            self.initialize()

    def discover_models(self):

        self.chat_models.clear()
        self.embedding_models.clear()

        for model in self.client.models.list():

            methods = (
                getattr(model, "supported_actions", None)
                or getattr(model, "supported_generation_methods", [])
            )

            if "generateContent" in methods:
                self.chat_models.append(model.name)

            if "embedContent" in methods:
                self.embedding_models.append(model.name)

        self.chat_models = [
            model
            for model in self.PREFERRED_MODELS
            if model in self.chat_models
        ]

    def find_best_chat_model(self):

        print()
        print("=" * 60)
        print("TESTING CHAT MODELS")
        print("=" * 60)

        for model in self.chat_models:

            print(model, end=" ... ")

            try:

                response = self.client.models.generate_content(
                    model=model,
                    contents="Reply only with OK."
                )

                if response.text:
                    print("SUCCESS")
                    self.chat_model = model
                    return model

            except Exception:

                print("FAILED")

        return None

    def find_embedding_model(self):

        preferred = "models/gemini-embedding-2"

        if preferred in self.embedding_models:
            self.embedding_model = preferred

        elif self.embedding_models:
            self.embedding_model = self.embedding_models[0]

        return self.embedding_model

    def save_models(self):

        data = {
            "chat_model": self.chat_model,
            "embedding_model": self.embedding_model
        }

        try:

            with open(self.models_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

            print()
            print("Models saved.")
            print(self.models_file)

            return True

        except Exception as ex:

            print(ex)
            return False

    def load_models(self):

        if not self.models_file.exists():
            return False

        try:

            with open(self.models_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.chat_model = data.get("chat_model")
            self.embedding_model = data.get("embedding_model")

            print()
            print("Models loaded.")
            print(self.models_file)

            return True

        except Exception as ex:

            print(ex)
            return False

    def get_client(self):
        """
        Returns the Gemini client.
        """
        return self.client

    def get_chat_model(self):
        """
        Returns the selected chat model.
        """
        return self.chat_model

    def get_embedding_model(self):
        """
        Returns the selected embedding model.
        """
        return self.embedding_model

    def initialize(self):

        self.discover_models()

        self.find_best_chat_model()

        self.find_embedding_model()

        print()
        print("Chat Model :", self.chat_model)
        print("Embedding :", self.embedding_model)

        self.save_models()

        return {
            "chat_model": self.chat_model,
            "embedding_model": self.embedding_model
        }


if __name__ == "__main__":

    manager = GeminiManager()

    print()
    print("=" * 60)
    print("SELECTED MODELS")
    print("=" * 60)

    print("Chat Model      :", manager.get_chat_model())
    print("Embedding Model :", manager.get_embedding_model())
