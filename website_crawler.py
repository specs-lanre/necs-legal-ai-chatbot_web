"""
=================================================

Knowledge Builder

Website Crawler

Downloads website pages and caches the HTML.

Version: 1.0

=================================================
"""
from urllib.parse import urlparse
import requests
from pathlib import Path
from config import Config
from logger import Logger
from website_discovery import WebsiteDiscovery

class WebsiteCrawler:
	def __init__(self):
		self.config = Config();self.logger = Logger()
		self.logger.info("Website Crawler initialized.")
		self.cache_folder = Path("website_cache")
		self.cache_folder.mkdir(exist_ok=True)
		self.logger.info(f"Cache Folder : {self.cache_folder}")
		self.cached_files = []
	def download_page(self, url):
		""" Downloads one webpage.Returns: HTML string """
		self.logger.info(f"Downloading : {url}")
		try:
			response = requests.get(url,timeout=30,headers={"User-Agent":"Mozilla/5.0 KnowledgeBuilder"})
			response.raise_for_status()
			self.logger.info("Download successful.")
			return response.text
		except Exception as ex:
			self.logger.error(f"Download failed : {ex}")
		return None
	def save_html(self, html, url):
		"""  Saves downloaded HTML into the website cache.
		Parameters  ----------
		html : str  Downloaded HTML.
		 url : str  Original webpage URL.
		 Returns-------  Path  Saved HTML file.
		"""
		if html is None:
			 return None
		try:
			parsed = urlparse(url)
			filename = parsed.path.strip("/")
			# Homepage
			if filename == "":
				filename = "index"
			# Replace "/" with "_"
			filename = filename.replace("/", "_")
			# Replace "-" with "_"
			filename = filename.replace("-", "_")
			filepath = self.cache_folder / f"{filename}.html"
			filepath.write_text(html,encoding="utf-8")
			self.logger.info(f"Saved : {filepath.name}")
			return filepath
		except Exception as ex:
			self.logger.error(f"Unable to save HTML : {ex}")
			return None
	def load_html(self, filepath):
		"""Loads a cached HTML file.Parameters----------
		filepath : Path  HTML file to read.  Returns ------- str
		HTML contents."""
		try:
			self.logger.info(f"Loading : {filepath.name}")
			html = filepath.read_text(encoding="utf-8")
			self.logger.info(f"Loaded {len(html)} characters.")
			return html
		except Exception as ex:
			self.logger.error(f"Unable to load HTML : {ex}")
			return None
	def download_all(self, urls):
		"""Downloads every webpage and saves it to the cache.
		Parameters  ----------  urls : list[str] Website page URLs.
		Returns   ------- list[Path]   Cached HTML files.  """
		self.logger.info("")
		self.logger.info("=" * 60)
		self.logger.info("DOWNLOADING WEBSITE")
		self.logger.info("=" * 60)
		self.cached_files.clear()
		total = len(urls)
		for index, url in enumerate(urls, start=1):
			self.logger.info(f"[{index}/{total}] {url}")
			html = self.download_page(url)
			if html is None:
				self.logger.warning(f"Skipping {url}")
				continue
			filepath = self.save_html(html, url)
			if filepath is not None:
				self.cached_files.append(filepath)
		self.logger.info("")
		self.logger.info(f"Downloaded {len(self.cached_files)} page(s).")
		return self.cached_files
		



if __name__ == "__main__":
	discovery = WebsiteDiscovery()
	urls = discovery.discover()
	crawler = WebsiteCrawler()
	url = "https://necs-legal.com/"
	html = crawler.download_page(url)
	files = crawler.download_all(urls)
	
	if html is not None:
		pass
		#print();print("=" * 60)
		#print("FIRST 1000 CHARACTERS")
		#print("=" * 60);print(html[:1000])
		
		'''
		filepath = crawler.save_html(html, url)
		print();print("=" * 60);print("FILE SAVED");print("=" * 60);print(filepath)
		print();print("=" * 60);print("READING FILE BACK"); print("=" * 60)
		html2 = crawler.load_html(filepath);print();print("Characters :", len(html2))
		print();print(html2[:500])
		'''
		print();print("=" * 60);print("DOWNLOADED FILES");print("=" * 60)
		for file in files:
			print(file);print();print("-" * 60); print(f"Total Files : {len(files)}")
    
    
    
    
    
    
    
    
    
    
    
