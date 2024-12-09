# src/utils/input_handler.py
import os
from urllib.parse import urlparse
from pathlib import Path
import asyncio
import logging
from src.utils.link_extractor import LinkExtractor
from src.utils.sitemap_parser import SitemapParser
from src.utils.crawler import WebCrawler
from src.utils.validation import URLValidator

logger = logging.getLogger(__name__)

class InputHandler:
    def __init__(self, file_manager):
        self.file_manager = file_manager
        self.link_extractor = LinkExtractor()
        self.sitemap_parser = SitemapParser()

    def guess_input_type(self, input_str: str) -> str:
        # Check if file
        p = self.file_manager.get_input_path(input_str)
        if p.exists() and p.is_file():
            # If it's a local sitemap
            if input_str.endswith("sitemap.xml"):
                return "local_sitemap_file"
            else:
                # Assume markdown if not sitemap.xml
                return "markdown_file"
        else:
            # Check if URL
            if URLValidator.is_valid_url(input_str):
                if input_str.endswith("sitemap.xml"):
                    return "remote_sitemap"
                else:
                    # base_url
                    return "base_url"
            else:
                # not a file, not a URL
                # Could be a markdown file not in INPUT_DIR or invalid input
                # We'll assume markdown if it's a relative path in INPUT_DIR
                # If it doesn't exist, will fail later
                return "markdown_file"

    async def fetch_urls(self, input_str: str) -> list:
        input_type = self.guess_input_type(input_str)
        logger.info(f"Determined input type: {input_type}")

        if input_type == "local_sitemap_file":
            p = self.file_manager.get_input_path(input_str)
            return self.sitemap_parser.parse_sitemap_file(str(p))

        elif input_type == "remote_sitemap":
            return await self.sitemap_parser.parse_sitemap_url(input_str)

        elif input_type == "base_url":
            # Crawl the base domain
            crawler = WebCrawler(input_str, max_pages=100)
            pages = await crawler.run()
            return pages

        else: # markdown_file
            p = self.file_manager.get_input_path(input_str)
            structure = self.link_extractor.extract_from_markdown(p)
            if not structure:
                return []
            return self.link_extractor.get_organized_links(structure)
