# src/utils/sitemap_parser.py
import logging
import aiohttp
import async_timeout
from bs4 import BeautifulSoup
import os

logger = logging.getLogger(__name__)

class SitemapParser:
    async def parse_sitemap_url(self, sitemap_url: str) -> list:
        """Fetch and parse a remote sitemap.xml URL."""
        try:
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(30):
                    async with session.get(sitemap_url) as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            return self.parse_sitemap_content(text)
                        else:
                            logger.warning(f"Failed to fetch sitemap from {sitemap_url}, status {resp.status}")
                            return []
        except Exception as e:
            logger.error(f"Error parsing remote sitemap {sitemap_url}: {e}")
            return []

    def parse_sitemap_file(self, filepath: str) -> list:
        """Parse a local sitemap.xml file."""
        if not os.path.exists(filepath):
            logger.error(f"Sitemap file not found: {filepath}")
            return []
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = f.read()
            return self.parse_sitemap_content(data)
        except Exception as e:
            logger.error(f"Error reading sitemap file {filepath}: {e}")
            return []

    def parse_sitemap_content(self, content: str) -> list:
        soup = BeautifulSoup(content, "lxml-xml")
        urls = [loc.get_text() for loc in soup.find_all("loc")]
        return urls
