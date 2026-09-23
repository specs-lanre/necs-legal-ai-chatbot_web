"""
=================================================

Knowledge Builder

Parser Module

Reads knowledge files and converts them into
Chunk objects.

Version 1.0

=================================================
"""
from pathlib import Path
from config import Config
from logger import Logger

class Chunk:
	def __init__(self):
		self.id = ""
		self.service = ""
		self.section = ""
		self.filename = ""
		self.text = ""
		self.metadata = {}
		self.embedding = None
		self.lookup_id = ""
		self.vector_index = -1
		self.word_count = 0
		self.metadata_path = None
		self.embedding_path = None
		self.manifest_path = None
		self.content_hash = ""
		
		
	def __str__(self):
		#return (f"Chunk("f"service='{self.service}',"f"section='{self.section}',"f"filename='{self.filename}',"f"words={self.word_count})" )
		return (
		"\n"
		f"Service     : {self.service}\n"
		f"Section     : {self.section}\n"
		f"Filename    : {self.filename}\n"
		f"Words       : {self.word_count}"
		f"Metadata       : {self.metadata_path.name}\n"
		f"Embedding      : {self.embedding_path.name}\n"
		f"Manifest       : {self.manifest_path.name}"
		)

class Parser:
	""" Parses chunk files. """
	def __init__(self):
		self.config = Config()
		self.logger = Logger()
		self.logger.info("Parser initialized.")
		self.chunks = []
	
	def parse(self, filepath: Path):
		"""Reads one knowledge file and returns a Chunk object."""
		self.logger.info(f"Reading {filepath.name}")
		chunk = Chunk()
		try:
			chunk.filepath = filepath;chunk.filename = filepath.name
			chunk.section = filepath.stem
			chunk.service = filepath.parent.parent.name
			service_folder = filepath.parent.parent
			chunk.metadata_path = (service_folder /"metadata"/f"{chunk.section}.json")
			chunk.embedding_path = (service_folder/"embeddings"/f"{chunk.section}.npy")
			chunk.manifest_path = (service_folder/"manifest.json")
			chunk.text = filepath.read_text(encoding="utf-8").strip();
			from hash_utils import HashUtils
			chunk.content_hash = HashUtils.sha256(chunk.text)
			chunk.word_count = len(chunk.text.split())
			if not chunk.text.strip():
				self.logger.warning(f"{filepath.name} is empty.")
				return None
			return chunk
		except Exception as ex:
			self.logger.error(f"Failed to read {filepath}: {ex}")
			return None
	def parse_files(self, filepaths):
		 """Parse multiple files. """
		 self.logger.info(f"Parsing {len(filepaths)} files.")
		 self.chunks.clear()
		 for filepath in filepaths:
			 chunk = self.parse_(filepath)
			 if chunk is not None:
				 self.chunks.append(chunk)
			 self.logger.info(f"Created {len(self.chunks)} chunks.");
		 return self.chunks
        
        
        
        
if __name__ == "__main__":
	chunk = Chunk();print(chunk);parser = Parser()
	path = Path("knowledge/services/trademarks/chunks/summary.txt")
	chunk = parser.parse(path);print(chunk.filename)
	print();print(chunk.text);print(chunk);print();
	print("Service :", chunk.service);print("Section :", chunk.section)
	print("Filename:", chunk.filename);print();print(chunk.text)
	from scanner import Scanner
	scanner = Scanner()
	scanner.scan();	parser = Parser()
	chunks = parser.parse_files(scanner.chunk_files)
	print();print("=" * 60);print(f"Chunks Created : {len(chunks)}");print("=" * 60)
	for chunk in chunks:
		print(chunk)
	print(chunk.content_hash)
