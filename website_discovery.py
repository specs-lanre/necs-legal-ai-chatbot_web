import requests
import xml.etree.ElementTree as ET

from config import Config
from logger import Logger


class WebsiteDiscovery:
	def __init__(self):
		self.config = Config()
		self.logger = Logger()
		self.raw_html_folder = self.config.knowledge_source_folder / "raw_html"
		self.raw_html_folder.mkdir(parents=True, exist_ok=True)
		self.logger.info("Website Crawler initialized.")
		self.sitemap_urls = []
		self.page_urls = []
		
	def download_sitemap(self):
		self.logger.info("Downloading sitemap...")
		response = requests.get(f"{self.config.website_url}/sitemap.xml",timeout=30)
		response.raise_for_status()
		self.logger.info("Sitemap downloaded successfully.")
		return response.text
	def parse_sitemap(self, xml_text):
		self.logger.info("Parsing sitemap...")
		self.sitemap_urls.clear()
		root = ET.fromstring(xml_text)
		namespace ={"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
		for sitemap in root.findall("sm:sitemap", namespace):
			location = sitemap.find("sm:loc", namespace)
			if location is not None:
				self.sitemap_urls.append(location.text)
			self.logger.info(f"Found {len(self.sitemap_urls)} sitemap(s).")
		return self.sitemap_urls
	def discover(self):
		xml = self.download_sitemap()
		return self.parse_sitemap(xml)
	
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
	def download_child_sitemap(self, url):
		"""Downloads one child sitemap.Returns the XML text."""
		self.logger.info(f"Downloading child sitemap : {url}")
		try:
			response = requests.get(url, timeout=30)
			response.raise_for_status()
			self.logger.info("Child sitemap downloaded successfully.")
			return response.text
		except Exception as ex:
			self.logger.error(f"Failed to download child sitemap : {ex}")
			return None
	def parse_child_sitemap(self, xml_text):
		"""Reads one child sitemap and extracts all page URLs."""
		if xml_text is None:
			return
		self.logger.info("Parsing child sitemap...")
		namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
		root = ET.fromstring(xml_text)
		count = 0
		for url in root.findall("sm:url", namespace):
			location = url.find("sm:loc", namespace)
			if location is not None:
				self.page_urls.append(location.text)
				self.page_urls.append(location.text)
				count += 1
		self.logger.info(f"Found {count} page(s).")
	def discover_pages(self):
		""" Downloads every child sitemap and extracts all website pages."""
		self.logger.info("");self.logger.info("=" * 60)
		self.logger.info("DISCOVERING WEBSITE PAGES")
		self.logger.info("=" * 60);self.page_urls.clear()
		for sitemap_url in self.sitemap_urls:
			xml = self.download_child_sitemap(sitemap_url)
			self.parse_child_sitemap(xml)
		self.logger.info(f"Total pages discovered : {len(self.page_urls)}")
		return self.page_urls
	def discover(self):
		""" Discovers all website pages."""
		xml = self.download_sitemap();self.parse_sitemap(xml)
		self.discover_pages();return self.page_urls

        


if __name__ == "__main__":	
	discovery = WebsiteDiscovery()
	sitemaps = discovery.discover()
	print()
	print("=" * 60);print("SITEMAPS FOUND");print("=" * 60)
	for sitemap in sitemaps:
		print(sitemap);print()
		print(f"Total : {len(sitemaps)}");pages = discovery.discover()
	print();print("=" * 60);print("WEBSITE PAGES DISCOVERED");print("=" * 60)
	for page in pages:
		print(page)
		print();
	print("-" * 60);
	print(f"Total Pages : {len(pages)}")
