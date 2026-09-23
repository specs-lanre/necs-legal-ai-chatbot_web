"""
=================================================

Knowledge Builder

Scanner Module

Scans the knowledge folder and discovers all files.

Version: 1.0

=================================================
"""
from pathlib import Path
from config import Config
from logger import Logger
class Scanner:
	"""Scans the knowledge folder. """
	def __init__(self):
		self.config = Config()
		self.logger = Logger()
		self.logger.info("Scanner initialized.")
		self.company_folders = []
		self.service_folders = []
		self.chunk_files = []
		self.metadata_files = []
		self.embedding_files = []
		self.manifest_files = []
	def scan(self):
		self.logger.info("Scanning knowledge folder...")
		print()
		print("Knowledge Folder")
		print(self.config.knowledge_folder)
		 # Clear previous scan results
		self.company_folders.clear();self.service_folders.clear()
		self.chunk_files.clear();self.metadata_files.clear()
		self.embedding_files.clear();self.manifest_files.clear()
		print();print(self.config.knowledge_folder)

		for item in self.config.knowledge_folder.rglob("*"):
			##print(item)
			if item.is_dir():
				print(f"DIR  : {item}")
			elif item.is_file():
				print(f"FILE : {item}")
				if item.name == "manifest.json":
					self.manifest_files.append(item)
				#elif item.suffix == ".txt":
					#self.chunk_files.append(item)
				elif (item.suffix == ".txt" and "chunks" in item.parts):
					self.chunk_files.append(item)
		print()
		print("=" * 50)
		print("SCAN SUMMARY")
		print("=" * 50)
		print(f"Chunk Files    : {len(self.chunk_files)}")
		print(f"Manifest Files : {len(self.manifest_files)}")
		return self.chunk_files
				
				
if __name__ == "__main__":
	scanner = Scanner()
	scanner.scan()











