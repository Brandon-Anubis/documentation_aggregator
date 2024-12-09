# src/web_clipper.py
import asyncio
import logging
from datetime import datetime
from typing import Optional, List
from src.processors.content_processor import ContentProcessor
from src.utils.file_manager import FileManager
from src.utils.input_handler import InputHandler
import os
from urllib.parse import urlparse
from src.utils.helpers import clean_text, url_to_filename
import aiohttp
from bs4 import BeautifulSoup
from config import USER_AGENT, MAX_CONCURRENT_REQUESTS, OUTPUT_DIR

logger = logging.getLogger(__name__)


class WebClipper:
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.file_manager = FileManager()
        self.content_processor = ContentProcessor()
        self.input_handler = InputHandler(self.file_manager)

        self.output_format = self.config.get("output_format", "markdown")
        self.include_metadata = self.config.get("include_metadata", True)
        self.output_dir = self.config.get("output_dir", OUTPUT_DIR)
        os.makedirs(self.output_dir, exist_ok=True)

    async def _fetch_content(self, url: str) -> tuple[str, str]:
        """Fetch title and raw text content from URL."""
        async with aiohttp.ClientSession(headers={"User-Agent": USER_AGENT}) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch URL: {response.status}")
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                title = soup.title.string if soup.title else url_to_filename(url)
                content = clean_text(soup.get_text())
                return title, content

    def _generate_filename(self, title: str, timestamp: str) -> str:
        """Generate a clean filename from title and timestamp."""
        clean_title = "".join(c if c.isalnum() or c in "-_ " else "_" for c in title)
        clean_title = clean_title.replace(" ", "-")[:50]
        return f"{clean_title}-{timestamp}"

    async def clip(
        self, url: str, result_id: str, tags: Optional[List[str]] = None
    ) -> dict:
        try:
            if url.endswith("sitemap.xml"):
                # Handle sitemap
                urls = await self.input_handler.fetch_urls(url)
                if not urls:
                    raise ValueError("No URLs found in sitemap")
                logger.info(f"Processing {len(urls)} URLs from sitemap")
                content_list = await self.process_urls(urls)
                if not content_list:
                    raise ValueError("No content was successfully aggregated")

                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                # Generate markdown
                final_doc = self.content_processor.generate_markdown(
                    content_list,
                    timestamp,
                    include_metadata=self.include_metadata,
                    tags=tags,
                )

                base_filename = self._generate_filename(
                    "aggregated_document", timestamp
                )
                markdown_filename = f"{base_filename}.md"
                markdown_path = os.path.join(self.output_dir, markdown_filename)
                with open(markdown_path, "w", encoding="utf-8") as f:
                    f.write(final_doc)

                pdf_filename = f"{base_filename}.pdf"  # PDF stub

                return {
                    "title": "Aggregated content",
                    "url": url,
                    "markdown_path": markdown_filename,
                    "pdf_path": pdf_filename,
                    "timestamp": timestamp,
                    "status": "completed",
                    "preview": (
                        final_doc[:500] + "..." if len(final_doc) > 500 else final_doc
                    ),
                }

            else:
                # Handle single URL
                title, raw_content = await self._fetch_content(url)
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

                # Extract and clean content (no heading prefix here)
                extracted_content = self.content_processor.extract_content(raw_content)
                content_item = {
                    "url": url,
                    "title": title,
                    "content": extracted_content,
                }
                content_list = [content_item]

                final_doc = self.content_processor.generate_markdown(
                    content_list,
                    timestamp,
                    include_metadata=self.include_metadata,
                    tags=tags,
                )

                base_filename = self._generate_filename(title, timestamp)
                markdown_filename = f"{base_filename}.md"
                markdown_path = os.path.join(self.output_dir, markdown_filename)
                with open(markdown_path, "w", encoding="utf-8") as f:
                    f.write(final_doc)

                pdf_filename = f"{base_filename}.pdf"  # PDF stub

                return {
                    "title": title,
                    "url": url,
                    "markdown_path": markdown_filename,
                    "pdf_path": pdf_filename,
                    "timestamp": timestamp,
                    "status": "completed",
                    "preview": (
                        final_doc[:500] + "..." if len(final_doc) > 500 else final_doc
                    ),
                }

        except ValueError as e:
            logger.error(f"Validation error in clip: {str(e)}")
            return {
                "title": url_to_filename(url),
                "url": url,
                "status": "failed",
                "error": str(e),
            }
        except Exception as e:
            logger.error(f"Error clipping content: {str(e)}")
            return {
                "title": url_to_filename(url),
                "url": url,
                "status": "failed",
                "error": "An unexpected error occurred while processing the content",
            }

    async def process_urls(self, urls: list) -> list:
        import async_timeout

        sem = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

        async def fetch_html(u):
            async with aiohttp.ClientSession(
                headers={"User-Agent": USER_AGENT}
            ) as session:
                async with sem:
                    try:
                        async with async_timeout.timeout(30):
                            async with session.get(u) as response:
                                if (
                                    response.status == 200
                                    and "text/html"
                                    in response.headers.get("Content-Type", "")
                                ):
                                    return await response.text()
                                else:
                                    logger.warning(f"Invalid content at {u}")
                                    return ""
                    except Exception as e:
                        logger.error(f"Error fetching {u}: {e}")
                        return ""

        async def process_url(u):
            html = await fetch_html(u)
            if not html:
                return None

            soup = BeautifulSoup(html, "html.parser")
            title_tag = soup.find("title")
            title = title_tag.get_text().strip() if title_tag else url_to_filename(u)

            # Extract and clean content without adding a heading
            content = self.content_processor.extract_content(html)
            if not content:
                return None

            return {
                "url": u,
                "title": title,
                "content": content,  # No added heading here
            }

        tasks = [process_url(u) for u in urls]
        res = await asyncio.gather(*tasks, return_exceptions=True)
        valid_results = []

        for r in res:
            if isinstance(r, Exception):
                logger.error(f"Error processing URL: {str(r)}")
            elif r is not None:
                valid_results.append(r)

        return valid_results
