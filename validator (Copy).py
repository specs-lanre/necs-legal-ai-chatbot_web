"""
=============================================

Knowledge Builder

Validator Module

Checks the integrity of the knowledge base.

=============================================
"""

from pathlib import Path
from config import Config
from logger import Logger

class ValidationResult:
	"""Stores the result of validating one chunk."""
	def __init__(self):
		self.chunk = None;self.passed = True;self.errors = [];self.warnings = []
	def add_error(self, message):
		self.errors.append(message);self.passed = False
	def add_warning(self, message):
		self.warnings.append(message)
	def __str__(self):
		return (
		f"Passed={self.passed}, "
		f"Errors={len(self.errors)}, " 
		f"Warnings={len(self.warnings)}" )


class Validator:
	""" Validates Chunk objects. """
	def __init__(self):
		self.config = Config();self.logger = Logger()
		self.logger.info("Validator initialized.")
	def validate_chunk(self, chunk):
		"""Validate one chunk."""
		self.logger.info(f"Validating {chunk.filename}")
		if not chunk.filepath.exists():
			#self.logger.error(f"{chunk.filepath} does not exist.")
			#return False
			result.add_error("Chunk file does not exist.")
			return result
		return True
		if chunk.word_count == 0:
			self.logger.warning(f"{chunk.filename} is empty.")
			return False
		if not chunk.metadata_path.parent.exists():
			#self.logger.error("Metadata folder missing.")
			#return False
			result.add_error("Metadata folder missing.")
			return result
		if not chunk.embedding_path.parent.exists():
			self.logger.error("Embeddings folder missing.")
			return False
		if not chunk.manifest_path.exists():
			self.logger.warning("manifest.json missing.")
			result.add_warning("manifest.json missing.")
			return result
	
