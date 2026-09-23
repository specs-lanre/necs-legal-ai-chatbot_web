
"""
=========================================
Knowledge Builder

Configuration Module

Loads and validates application settings.

=========================================
"""


from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv()

DB_URL = os.getenv("DB_URL")
DEBUG = os.getenv("DEBUG")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-3.5-flash"


class Config():
	def __init__(self):
		
		"""
		Stores all application configuration.
		"""
		#self.gemini_chat_model = "models/gemini-3.5-flash"
		self.gemini_chat_model = "models/gemini-3.5-flash-lite"
		self.gemini_fast_model = "models/gemini-3.5-flash-lite"
		self.gemini_embedding_model = "models/gemini-embedding-2"
		self.gemini_api_key = os.getenv("GEMINI_API_KEY")
		self.embedding_model = os.getenv("EMBEDDING_MODEL")
		self.log_level = os.getenv("LOG_LEVEL")
		self.knowledge_folder = Path(os.getenv("KNOWLEDGE_FOLDER"))
		self.output_folder = Path(os.getenv("OUTPUT_FOLDER"))
		self.search_folder = Path(os.getenv("SEARCH_FOLDER"))
		self.logs_folder = Path(os.getenv("LOGS_FOLDER"))
		self.website_url = os.getenv("WEBSITE_URL")
		self.knowledge_source_folder = Path(os.getenv("KNOWLEDGE_SOURCE_FOLDER"))
		#this is a list of directories to be created
		self.required_directories = [
		self.knowledge_folder,self.output_folder,self.search_folder, self.logs_folder,]
		self.test_folder = Path("test_folder")
		self.validate()
		self.create_directories()
	def validate(self):
				"""
					Validate the application configuration.
				"""
				if not self.gemini_api_key:
					raise ValueError("GEMINI_API_KEY is missing from the .env file.")
	
	
	def create_directories(self):
			"""
			Create required project directories.
			"""
			for folder in self.required_directories:
				folder.mkdir(parents=True,exist_ok=True)
				print(f"✓ Directory ready : {folder}")
				
			'''instead of the following lines of code we use the above'''

			'''self.knowledge_folder.mkdir(
				parents=True,
				exist_ok=True
			)

			self.output_folder.mkdir(
				parents=True,
				exist_ok=True
			)

			self.search_folder.mkdir(
				parents=True,
				exist_ok=True
			)'''
			"""creates test_folder in the calling location"""
			self.test_folder.mkdir(
				parents=True,
				exist_ok=True
			)
			
			
			
        
        
        	
if __name__ == "__main__":
	config = Config()
	print("Config object created successfully.")
	
	print(config.gemini_api_key)
	print(config.knowledge_folder.exists())
	print(config.embedding_model)
	print(config.output_folder.exists())
	print(config.search_folder.exists())









