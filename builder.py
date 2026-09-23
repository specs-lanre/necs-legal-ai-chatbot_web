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
		self.config = Config()
		self.logger = Logger()
		self.scanner = Scanner()
		self.parser = Parser()
		self.validator = Validator()
		self.metadata = MetadataManager()
		self.embedding = EmbeddingBuilder()
		self.lookup = LookupBuilder()
		self.faiss = FaissBuilder();
		
		# Working data
		self.files = [];self.chunks = [];self.vectors = []
		self.logger.info("Master Builder initialized.")
	def scan(self):
		self.logger.info("");self.logger.info("=" * 60)
		self.logger.info("STEP 1 : SCANNING KNOWLEDGE")
		self.logger.info("=" * 60)
		self.files = self.scanner.scan()
		self.logger.info(f"{len(self.files)} text files found.")
		return self.files
		
	def parse(self):
		self.logger.info("");self.logger.info("=" * 60)
		self.logger.info("STEP 2 : PARSING CHUNKS")
		self.logger.info("=" * 60);self.chunks.clear()
		for filepath in self.files:
			chunk = self.parser.parse(filepath)
			if chunk is not None:
				self.chunks.append(chunk)
		self.logger.info(f"{len(self.chunks)} chunk(s) parsed.")
		return self.chunks
		
	def build(self):
		self.logger.info("Starting knowledge build...")
		
		self.scan()
		self.parse()
		
		self.logger.info(f"{len(self.files)} chunk file(s) found.")
		self.vectors.clear()
		for chunk in self.chunks:			
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
			self.vectors.append(chunk.embedding)
		self.lookup.save()
		if not self.vectors:
			self.logger.error("No embeddings were generated.")
			return
		matrix = np.array(self.vectors,dtype="float32")
		dimension = matrix.shape[1]
		self.faiss.create_index(dimension)
		self.faiss.add_embeddings(matrix)		
		self.faiss.save()
		self.logger.info(f"Build Complete.")
		self.logger.info(f"Chunks : {len(self.vectors)}")
		self.logger.info(f"Dimensions : {dimension}")
		
        
if __name__ == "__main__":
	builder = Builder()
	builder.scan()
	builder.parse()
	print();print("=" * 60);print("FIRST PARSED CHUNK");print("=" * 60)
	chunk = builder.chunks[0]
	print("Filename       :", chunk.filename)
	print("Section        :", chunk.section)
	print("Service        :", chunk.service)
	print("Word Count     :", chunk.word_count)
	print("Hash           :", chunk.content_hash[:20])
	print("Metadata Path  :", chunk.metadata_path)
	print("Embedding Path :", chunk.embedding_path)
