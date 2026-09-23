"""
===============================================

Knowledge Builder

Main Builder Module

Coordinates the complete knowledge-building process.

Version: 1.0

===============================================
"""
from config import Config
from logger import Logger

class Builder:
	""" Coordinates the Knowledge Builder."""
	def __init__(self):
		self.config = Config()
		self.logger = Logger()
		self.logger.info("Builder initialized.")
	def build(self):
		self.logger.info("Knowledge Build Started")
		print()
		print("=" * 60)
		print("Knowledge Builder")
		print("=" * 60)
		


if __name__ == "__main__":
	builder = Builder()
	builder.build()
