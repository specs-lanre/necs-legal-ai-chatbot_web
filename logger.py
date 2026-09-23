"""
=================================================

Knowledge Builder

Logger Module

Creates the application logger.

Author:

Version : 1.0

=================================================
"""

import logging
from pathlib import Path
from config import Config

config = Config()
log_folder = config.logs_folder
class Logger:
	def __init__(self):
		self.config = Config()
		print("Logger object created.")
		self.logger = logging.getLogger("KnowledgeBuilder")
		self.logger.setLevel(logging.INFO)
		self.log_file = self.config.logs_folder / "builder.log"
		print(f"Logger initialized \n\r .Log File : {self.log_file}")
		self.file_handler = logging.FileHandler(self.log_file)
		self.formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
		self.file_handler.setFormatter(self.formatter)
		#self.logger.addHandler(self.file_handler)
		self.console_handler = logging.StreamHandler()
		self.console_handler.setFormatter(self.formatter)
		#self.logger.addHandler(self.console_handler)
		#the following line prevents multiple added handlers from running repeatitively
		if not self.logger.handlers:
						self.logger.addHandler(self.file_handler)
						self.logger.addHandler(self.console_handler)
		
		
		
	def info(self,message):
		self.logger.info(message)
	def warning(self,message):
		self.logger.warning(message)
	def error(self,message):
		self.logger.error(message)
	def debug(self,message):
		self.logger.debug(message)
	


        
if __name__ == "__main__":

    print("=" * 50)
    print("Testing Logger")
    print("=" * 50)

    log = Logger()
    print(log.logger)
    #the following line writes the message below to the 
    #log file (builder.log)create above  
    log.logger.info("Knowledge Builder Started")
    log.info("Application Started")
    log.warning("Testing Warning")
    log.error("Testing Error")
    log.debug("Testing Debug")      


