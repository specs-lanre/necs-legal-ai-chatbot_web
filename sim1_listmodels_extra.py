from google import genai
from dotenv import load_dotenv
import os



if __name__ == "__main__":
		load_dotenv()

		client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
		for model in client.models.list():
			print("=" * 60)
			print(model.name)
			print(model.supported_actions)
