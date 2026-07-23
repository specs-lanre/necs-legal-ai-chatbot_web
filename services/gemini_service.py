from google import genai
from config import GEMINI_API_KEY , GEMINI_MODEL
from services.knowledge_service import load_knowledge

client = genai.Client(api_key=GEMINI_API_KEY)


def ask_gemini(message: str) -> str:
	try:
		knowledge = load_knowledge()
		prompt = f"""
				{knowledge}

				Visitor Question:

				{message}

				Answer as NECS Legal.
				"""
		response = client.models.generate_content(model=GEMINI_MODEL,contents=prompt)
		return response.text
	except ClientError as e:
			return f"Gemini API Error: {e}"
