'''
This version downloaded only the sitemap.
'''

from pathlib import Path
import requests

from config import Config
from logger import Logger


class WebsiteCrawler:
	def __init__(self):
		self.config = Config()
		self.logger = Logger()
		self.raw_html_folder = self.config.knowledge_source_folder / "raw_html"
		self.raw_html_folder.mkdir(parents=True, exist_ok=True)
		self.logger.info("Website Crawler initialized.")
	def download_page(self, url):
		self.logger.info(f"Downloading {url}")
		response = requests.get(url, timeout=30)
		response.raise_for_status()
		return response.text
	def save_html(self, html, filename):
		filepath = self.raw_html_folder / filename
		filepath.write_text(html, encoding="utf-8")
		self.logger.info(f"Saved {filepath}")
		return filepath

        


if __name__ == "__main__":
	crawler = WebsiteCrawler()
	html = crawler.download_page("https://necs-legal.com")
	crawler.save_html(html, "home.html")
	print();print("=" * 60);print("DOWNLOAD COMPLETE")
	print("=" * 60)
