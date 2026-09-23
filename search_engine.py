from pathlib import Path
from config import Config
from logger import Logger
from embedding_builder import EmbeddingBuilder
from lookup_builder import LookupBuilder
from faiss_builder import FaissBuilder


class SearchEngine:
	""" Semantic search engine. """ 
	def __init__(self):
		self.config = Config()
		self.logger = Logger()
		self.embedding_builder = EmbeddingBuilder()
		self.lookup_builder = LookupBuilder()
		self.faiss_builder = FaissBuilder()
		
		self.lookup_builder.load()
		self.faiss_builder.load()
		print("FAISS dimension:", self.faiss_builder.dimension())
		self.logger.info("Search Engine initialized.")
	def embed_question(self, question):
		self.logger.info("Embedding question...")
		return self.embedding_builder.generate_embedding(question)
	def search(self, question, top_k=5):
		vector = self.embed_question(question)
		print("Question dimension:", len(vector))
		distances, indexes = self.faiss_builder.search(vector,top_k)
		return distances, indexes
	def retrieve_chunks(self, indexes):
		chunks = []
		for index in indexes[0]:
			record = self.lookup_builder.get(index)
			filepath = Path(record["filepath"])
			text = filepath.read_text(encoding="utf-8")
			chunks.append({"record": record,"text": text})
		return chunks
	def dimension(self):
		return self.index.d

if __name__ == "__main__":
	engine = SearchEngine()
	results = engine.search("Can you register my trademark?")
	for result in results:
		print("=" * 60)
		print(result["record"]["filename"])
		print();print(result["text"][:300])
        
        
        
