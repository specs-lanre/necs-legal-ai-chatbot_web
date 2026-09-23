"""
=================================================

Knowledge Builder

HTML Cleaner

Extracts useful content from downloaded HTML.

Version: 1.0

=================================================
"""
import re
from pathlib import Path
from bs4 import BeautifulSoup

from config import Config
from logger import Logger


class HtmlCleaner:
	def __init__(self):
		self.config = Config();self.logger = Logger()
		self.logger.info("HTML Cleaner initialized.")
		self.cache_folder = Path("website_cache")
		self.output_folder = Path("clean_text")
		self.output_folder.mkdir(exist_ok=True)
		self.cleaned_files = []
		self.ignore_words = self.load_ignore_words()
	def load_html(self, filepath: Path):
		"""
		Loads a cached HTML file. Parameters  ---------- filepath : Path
		HTML file to load.   Returns    -------    str    HTML content."""
		self.logger.info(f"Loading HTML : {filepath.name}")
		try:
			html = filepath.read_text(encoding="utf-8",errors="ignore")
			self.logger.info(f"Loaded {len(html):,} characters.")
			return html
		except Exception as ex:self.logger.error(f"Unable to load {filepath.name} : {ex}");return None
	def extract_main_content(self, html):
		"""Extracts the main readable content from HTML.
		Parameters----------html : str  Returns  -------  str"""
		self.logger.info("Extracting main content...")
		try:
			soup = BeautifulSoup(html, "html.parser")
			# Remove unwanted tags completely
			for tag in soup(["script","style","noscript","iframe","svg","canvas","footer","header","nav","aside","form"]):
				tag.decompose()
			# ---------- WordPress Content ----------
			selectors = ["main","article", ".entry-content",".post-content",
			".page-content",".elementor-widget-theme-post-content",".elementor-location-single",
			"#content",".site-content" ]
			content = None
			for selector in selectors:
				content = soup.select_one(selector)
				if content is not None:
					self.logger.info(f"Content found using '{selector}'")
					break
			if content is None:
				self.logger.warning("No content selector matched. Using body.")
				content = soup.body
			if content is None:
				self.logger.error("No readable content found.")
				return None
			text = content.get_text(separator="\n",strip=True)
			self.logger.info(f"Extracted {len(text):,} characters.")
			return text
		except Exception as ex:
			self.logger.error(f"Extraction failed : {ex}")
			return None
	
	def clean_text(self, text):
		"""Cleans extracted website text. Parameters  ---------- text : str  Returns  -------   str  """
		self.logger.info("Cleaning extracted text...")
		if text is None:
			return None
		# ----------------------------------
		# Normalize line endings
		# ----------------------------------
		text = text.replace("\r\n", "\n");text = text.replace("\r", "\n")
		# ----------------------------------
		# Split into lines
		# ----------------------------------
		lines = text.split("\n");cleaned = [];previous = ""
		# --------# Words/Phrases to ignore--------------
		ignore = self.ignore_words
		# ------# Clean every line # --------------
		for line in lines:
			 line = line.strip()
			 if line == "":
				 continue
				 # Remove duplicate consecutive lines
			 if line == previous:
				 continue
			 previous = line
			 # Ignore navigation words
			 #if line.lower() in ignore:continue;
			 lower = line.lower();skip = False
			 for word in ignore:
				 if word in lower:skip = True;break
			 if skip:continue;				 
				 
			 # Ignore very short junk
			 if len(line) == 1:
				 continue
			 if line.isdigit():continue;
			 if len(line) < 2:continue;
			 cleaned.append(line)
		# --# Join back together # ---------
		text = "\n\n".join(cleaned)
		# ----# Collapse excessive spaces # ---------
		text = re.sub(r"[ \t]+", " ", text)
		# ----# Collapse too many blank lines# --------
		text = re.sub(r"\n{3,}", "\n\n", text)
		self.logger.info(f"Clean text length : {len(text):,} characters." )
		return text
	def load_ignore_words(self):
		""" Loads ignored words/phrases from file.Returns-------set"""
		filepath = Path("config/ignore_words.txt");ignore = set()
		try:
			for line in filepath.read_text(encoding="utf-8").splitlines():
				line = line.strip().lower()
				if line == "":continue;
				if line.startswith("#"):continue;
				ignore.add(line)
			self.logger.info(f"Loaded {len(ignore)} ignore words.");return ignore
		except Exception as ex:self.logger.error(f"Unable to load ignore words : {ex}");return set()
	def save_text(self, text, html_filepath: Path):
		"""Saves cleaned text into the clean_text folder
		.--Parameters------text : str Cleaned text.
		html_filepath : Path  Original HTML file.
		Returns-------Path"""
		if text is None:
			return None
		try:
			filename = html_filepath.stem + ".txt"
			output_path = self.output_folder / filename
			output_path.write_text(text,encoding="utf-8")
			self.cleaned_files.append(output_path)
			self.logger.info(f"Saved : {output_path.name}")
			return output_path
		except Exception as ex:
			self.logger.error(f"Unable to save {html_filepath.name} : {ex}")
			return None
	def clean_all(self):
		"""Cleans every HTML file in the website cache.	Returns	-------	list[Path]
		"""
		self.logger.info("");self.logger.info("=" * 60)
		self.logger.info("CLEANING WEBSITE")
		self.logger.info("=" * 60)
		self.cleaned_files.clear()
		html_files = sorted(self.cache_folder.glob("*.html"))
		self.logger.info(f"Found {len(html_files)} HTML files.")
		for index, filepath in enumerate(html_files, start=1):
			self.logger.info(f"[{index}/{len(html_files)}] {filepath.name}")
			html = self.load_html(filepath)
			if html is None:
				continue
			text = self.extract_main_content(html)
			if text is None:
				continue
			clean = self.clean_text(text)
			if clean is None:
				continue
			self.save_text(clean, filepath)
		self.logger.info("")
		self.logger.info(f"Generated {len(self.cleaned_files)} cleaned file(s).")
		return self.cleaned_files
	def process_all(self):
		"""Processes the entire website cache.Returns ------list[Path]	Cleaned text files.
		"""
		self.logger.info("")
		self.logger.info("=" * 60)
		self.logger.info("HTML CLEANER")
		self.logger.info("=" * 60)
		files = self.clean_all()
		self.logger.info("")
		self.logger.info("=" * 60)
		self.logger.info("HTML CLEANING COMPLETE")
		self.logger.info("=" * 60)
		self.logger.info(f"Files Generated : {len(files)}")
		return files




if __name__ == "__main__":
	cleaner = HtmlCleaner()
	filepath = Path("website_cache/index.html")
	html = cleaner.load_html(filepath)
	'''
	if html:
		print();print("=" * 60);print("FIRST 800 CHARACTERS")
		print("=" * 60);print(html[:800]);print();
		print("=" * 60);print(f"TOTAL CHARACTERS : {len(html):,}")
	text = cleaner.extract_main_content(html)
	print();print("=" * 60);print("EXTRACTED CONTENT");
	print("=" * 60);
	print(text[:3000])
	clean = cleaner.clean_text(text)
	print();print("=" * 60);print("CLEAN TEXT");print("=" * 60)
	print(clean[:4000])
	'''
	html = cleaner.load_html(filepath)
	text = cleaner.extract_main_content(html)
	clean = cleaner.clean_text(text)
	saved = cleaner.save_text(clean, filepath)
	print();print("=" * 60);print("FILE SAVED");print("=" * 60);print(saved)
	
	files = cleaner.clean_all()
	'''
	print();print("=" * 60);print("CLEANED FILES");print("=" * 60)
	for file in files:
		print(file);print();print(f"Total Files : {len(files)}")
		'''
		
	files = cleaner.process_all()
	print();print("=" * 60);print("GENERATED TEXT FILES");print("=" * 60)
	for file in files:
		print(file);print()
	print(f"Total Files : {len(files)}")
    
