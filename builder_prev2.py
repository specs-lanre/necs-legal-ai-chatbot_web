"""
==========================================
Knowledge Builder

Master Build Program

==========================================
"""

import numpy as np

from config import Config
from logger import Logger

from scanner import Scanner
from parser import Parser
from validator import Validator
from metadata_manager import MetadataManager
from embedding_builder import EmbeddingBuilder
from lookup_builder import LookupBuilder
from faiss_builder import FaissBuilder

class Builder:
	def __init__(self):
		self.config = Config();self.logger = Logger()
		self.scanner = Scanner();self.parser = Parser()
		self.validator = Validator();self.metadata = MetadataManager()
		self.embedding = EmbeddingBuilder();self.lookup = LookupBuilder()
		self.faiss = FaissBuilder();self.logger.info("Master Builder initialized.")
	def build(self):
		self.logger.info("Starting knowledge build...")
		files = self.scanner.scan()
		self.logger.info(f"{len(files)} chunk(s) found.")
		vectors = []
		for file in files:
			chunk = self.parser.parse(file)
			if chunk is None:
				continue
			if not self.validator.validate(chunk):
				self.logger.warning(f"Skipping {chunk.filename}")
				continue
			if self.metadata.embedding_is_current(chunk):
				self.embedding.load_embedding(chunk)
			else:
				chunk.embedding = self.embedding.generate_embedding(chunk.text)
				self.embedding.save_embedding(chunk)
				chunk.metadata = self.metadata.create_metadata(chunk)
				chunk.metadata["embedding_dimensions"] = len(chunk.embedding)
				self.metadata.save_metadata(chunk)
			self.lookup.add_chunk(chunk)
			vectors.append(chunk.embedding)
			self.lookup.save()
			matrix = np.array(vectors,dtype="float32")
			dimension = matrix.shape[1]
			self.faiss.create_index(dimension)
			self.faiss.add_embeddings(matrix)
			#self.faiss.index.add(matrix)
			self.faiss.save()
			self.logger.info(f"Build Complete.")
			self.logger.info(f"Chunks : {len(vectors)}")
			self.logger.info(f"Dimensions : {dimension}")
	def add_embeddings(self, matrix):
		self.index.add(matrix)
		self.logger.info( f"Added {matrix.shape[0]} embeddings to FAISS.")
		
        
if __name__ == "__main__":
	builder = Builder()
	builder.scan()
