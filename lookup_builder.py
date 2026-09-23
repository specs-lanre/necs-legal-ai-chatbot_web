import json

from config import Config
from logger import Logger

class LookupBuilder:
	"""  Builds the lookup table for FAISS.    """
	def __init__(self):
		self.config = Config();self.logger = Logger();self.lookup = []
		self.logger.info("Lookup Builder initialized.")
	def add_chunk(self, chunk):
		record = {
		"id": len(self.lookup), "service": chunk.service,
		"section": chunk.section,"filename": chunk.filename,
		"filepath": str(chunk.filepath),
		"embedding": str(chunk.embedding_path),
		"metadata": str(chunk.metadata_path)
		}
		self.lookup.append(record)
		self.logger.info(f"Added {chunk.filename} to lookup.")
	def save(self):
		output_file = self.config.search_folder / "lookup.json"
		with open(output_file,"w",encoding="utf-8") as file:
			json.dump(self.lookup,file,indent=4,ensure_ascii=False)
			self.logger.info(f"Lookup saved ({len(self.lookup)} records)")
	def load(self):
		input_file = self.config.search_folder / "lookup.json"
		with open(input_file,"r",encoding="utf-8") as file:
			self.lookup = json.load(file)
			self.logger.info( f"Loaded {len(self.lookup)} lookup records.")
		return self.lookup
	def get(self, index):
		return self.lookup[index]


if __name__ == "__main__":
	builder = LookupBuilder()
	class DummyChunk:
		pass
	chunk = DummyChunk()
	chunk.service = "trademark"
	chunk.section = "summary"
	chunk.filename = "summary.txt"
	chunk.filepath = "knowledge/services/trademark/chunks/summary.txt"
	chunk.embedding_path = "knowledge/services/trademark/embeddings/summary.npy"
	chunk.metadata_path = "knowledge/services/trademark/metadata/summary.json"
	builder.add_chunk(chunk);builder.save();builder.load();print(builder.get(0))
    
    
    
