#testing for embedding
from google import genai

from dotenv import load_dotenv
import os
# Load the .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)


if __name__ == "__main__":
	contents =input("Ask your question : ")
	response = client.models.embed_content(model="gemini-embedding-2",contents=contents)
	vector = response.embeddings[0].values
	print(len(vector))
	print("=================================")
	print(vector)
