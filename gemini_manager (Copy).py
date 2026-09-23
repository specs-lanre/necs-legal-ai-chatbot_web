from google import genai
from dotenv import load_dotenv
import os

load_dotenv()


class GeminiManager:
	def __init__(self):
		self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
		self.chat_model = None
		self.embedding_model = None
	def discover_models(self):
		self.chat_models = []
		self.embedding_models = []
		PREFERRED_MODELS = ["models/gemini-3.5-flash-lite","models/gemini-3.5-flash","models/gemini-2.5-flash",
		"models/gemini-2.0-flash","models/gemma-4-26b-a4b-it"]
		available = set()
		for model in self.client.models.list():
			available.add(model.name)
			self.chat_models = [model for model in PREFERRED_MODELS  if model in available]

		for model in self.client.models.list():
			methods = (getattr(model, "supported_actions", None)
			or getattr(model, "supported_generation_methods", []))
			if "generateContent" in methods:
				self.chat_models.append(model.name)
			if "embedContent" in methods:
				self.embedding_models.append(model.name)
	def find_best_chat_model(self):
		print();print("="*60);print("TESTING CHAT MODELS")
		print("="*60);
		for model in self.chat_models:
			print(model)
			try:
				response = self.client.models.generate_content(model=model,contents="Reply only with OK.")
				if response.text:
					self.chat_model = model
					print("SUCCESS")
					return model
			except Exception:
				print("FAILED")
		return None
	def find_embedding_model(self):
		if "models/gemini-embedding-2" in self.embedding_models:
			self.embedding_model = "models/gemini-embedding-2"
		elif self.embedding_models:
			self.embedding_model = self.embedding_models[0]
		return self.embedding_model
	def initialize(self):
		self.discover_models()
		self.find_best_chat_model()
		self.find_embedding_model()
		print();print("Chat Model");print(self.chat_model)
		print();print("Embedding Model");print(self.embedding_model)
		return {"chat_model": self.chat_model, "embedding_model": self.embedding_model}
		



if __name__ == "__main__":
	manager = GeminiManager()
	models = manager.initialize()
	print();print("=" * 60);print("SELECTED MODELS");print("=" * 60);print(models)
