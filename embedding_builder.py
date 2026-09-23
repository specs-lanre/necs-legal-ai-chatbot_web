"""
============================================

Knowledge Builder

Embedding Builder

Generates Gemini embeddings
for every knowledge chunk.

============================================
"""
import numpy as np
from google import genai
from config import Config
from logger import Logger


class EmbeddingBuilder:
	""" Generates embeddings using Gemini. """
	def __init__(self):
		self.config = Config()
		self.logger = Logger()
		self.client = genai.Client(api_key=self.config.gemini_api_key)
		self.logger.info("Embedding Builder initialized.")
	def generate_embedding(self, text):
		"""Generate one embedding."""
		response = self.client.models.embed_content(model=self.config.embedding_model,contents=text)
		return np.array(response.embeddings[0].values,dtype="float32")
	def save_embedding(self, chunk):
		np.save(chunk.embedding_path,chunk.embedding)
		self.logger.info(f"Saved {chunk.embedding_path.name}" )
	def load_embedding(self, chunk):
		if chunk.embedding_path.exists():
			chunk.embedding = np.load(chunk.embedding_path)
			self.logger.info(f"Loaded {chunk.embedding_path.name}")
			return True
		return False
	def build_chunk_embedding(self, chunk):
		'''
		if self.load_embedding(chunk):
			return chunk
		chunk.embedding = self.generate_embedding(chunk.text)
		self.save_embedding(chunk)
		return chunk'''
		if metadata_manager.embedding_is_current(chunk):
			if self.load_embedding(chunk):
				return chunk
			# Otherwise generate a fresh embedding
			chunk.embedding = self.generate_embedding(chunk.text)
			# Update metadata
			chunk.metadata = metadata_manager.create_metadata(chunk)
			chunk.metadata["embedding_dimensions"] = len(chunk.embedding)
			chunk.metadata["embedding_date"] = datetime.now().isoformat()
			self.save_embedding(chunk)
			metadata_manager.save_metadata(chunk)
			return chunk
		
		
		
		
		
		
if __name__ == "__main__":
	builder = EmbeddingBuilder()
	vector = builder.generate_embedding("Can you register my trademark?")
	print(type(vector))
	print(vector.shape)
	print(vector[:10])
	print(f"Data Type : {vector.dtype}")
	print("\nFirst 10 values:")
	print(vector[:10])
