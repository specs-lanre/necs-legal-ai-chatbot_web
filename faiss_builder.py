import faiss
import numpy as np
from pathlib import Path
from config import Config
from logger import Logger

class FaissBuilder:
	"""Builds the FAISS index."""
	def __init__(self):
		self.config = Config()
		self.logger = Logger()
		self.index = None
		self.logger.info("FAISS Builder initialized.")
	def create_index(self, dimension):
		self.index = faiss.IndexFlatL2(dimension)
		self.logger.info(f"Created FAISS index ({dimension} dimensions)")
	def add_embedding(self, vector):
		vector = np.array([vector],dtype="float32")
		self.index.add(vector)
	def save(self):
		output = self.config.search_folder / "faiss.index"
		faiss.write_index(self.index,str(output))
		self.logger.info("FAISS index saved.")
	def load(self):
		input_file = self.config.search_folder / "faiss.index"
		self.index = faiss.read_index(str(input_file))
		self.logger.info("FAISS index loaded.")
	def count(self):
		return self.index.ntotal
	def search(self, question_vector, top_k=5):
		question_vector = np.array([question_vector],dtype="float32" )
		distances, indexes = self.index.search(question_vector,top_k)
		return distances, indexes


if __name__ == "__main__":
	builder = FaissBuilder()
	builder.create_index(4)
	builder.add_embedding(np.array([1,2,3,4],dtype="float32") )
	builder.add_embedding(np.array([2,3,4,5],dtype="float32") )
	builder.add_embedding(np.array([10,11,12,13],dtype="float32") )
	print(builder.count())
	builder.save()
	builder.load()
	distances, indexes = builder.search(np.array([1,2,3,4],dtype="float32"),top_k=3)
	print(distances)
	print(indexes)
    
    
