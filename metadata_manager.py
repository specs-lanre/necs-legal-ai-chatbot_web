"""
=========================================

Knowledge Builder

Metadata Manager

Loads, validates and updates metadata.

=========================================
"""
import json
from datetime import datetime

from config import Config
from logger import Logger
class MetadataManager:
	"""Handles metadata operations."""
	def __init__(self):
		self.config = Config();self.logger = Logger();self.logger.info("Metadata Manager initialized.")
	def create_metadata(self, chunk):
		metadata = {"service": chunk.service,"section": chunk.section,"filename": chunk.filename,
		"content_hash": chunk.content_hash,"embedding_model": self.config.embedding_model,
		"embedding_date": None,"embedding_dimensions": None,"word_count": chunk.word_count,
		"created_at": datetime.now().isoformat(),"updated_at": datetime.now().isoformat() }
		return metadata
	def save_metadata(self, chunk):
		chunk.metadata["updated_at"] = (datetime.now().isoformat())
		with open(chunk.metadata_path,"w",encoding="utf-8") as file:
			json.dump(chunk.metadata,file,indent=4,ensure_ascii=False)
			self.logger.info(f"Saved {chunk.metadata_path.name}")
	def load_metadata(self, chunk):
		if not chunk.metadata_path.exists():
			return None
			with open(chunk.metadata_path,"r",encoding="utf-8") as file:
				chunk.metadata = json.load(file)
				self.logger.info(f"Loaded {chunk.metadata_path.name}")
				return chunk.metadata
	def embedding_is_current(self, chunk):
		metadata = self.load_metadata(chunk)
		if metadata is None:
			return False
		if metadata.get("content_hash") != chunk.content_hash:
			return False
		if metadata.get("embedding_model") != self.config.embedding_model:
			return False
		return True



