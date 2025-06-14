"""
WebClipper class for fetching and processing web content.
"""

import asyncio
from datetime import datetime
import logging
import os
from typing import List, Optional

import aiohttp
import async_timeout
from bs4 import BeautifulSoup
from playwright.async_api import Error as PlaywrightError

from config import (
    MAX_CONCURRENT_REQUESTS,
    OUTPUT_DIR,
    USER_AGENT,
    USE_PLAYWRIGHT_FOR_JS_CONTENT,
)
from src.processors.content_processor import ContentProcessor
from src.utils.crawler import WebCrawler
from src.utils.file_manager import FileManager
from src.utils.helpers import url_to_filename
from src.utils.input_handler import InputHandler

logger = logging.getLogger(__name__)


class WebClipper:
    """WebClipper class for fetching and processing web content."""

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.file_manager = FileManager()
        self.content_processor = ContentProcessor()
        self.input_handler = InputHandler(self.file_manager)

        self.output_format = self.config.get("output_format", "markdown")
        self.include_metadata = self.config.get("include_metadata", True)
        self.output_dir = self.config.get("output_dir", OUTPUT_DIR)
        os.makedirs(self.output_dir, exist_ok=True)

    async def _fetch_content(self, url: str) -> Optional[tuple[str, str]]:
        """Fetch title and HTML content from URL, using Playwright or aiohttp."""
        html_content = None
        if USE_PLAYWRIGHT_FOR_JS_CONTENT:
            logger.info(f"Fetching {url} with Playwright via WebClipper._fetch_content")
            crawler = WebCrawler(base_url=url)  # Instantiate WebCrawler locally
            try:
                html_content = await crawler.fetch_with_playwright(url)
                if not html_content:
                    logger.warning(
                        f"Playwright failed to fetch {url} in WebClipper._fetch_content, returning None."
                    )
                    return None
            except PlaywrightError as e:
                logger.error(
                    f"Playwright error in WebClipper._fetch_content for {url}: {e}"
                )
                return None
            except asyncio.TimeoutError:
                logger.error(
                    f"Playwright timeout in WebClipper._fetch_content for {url}"
                )
                return None
            except Exception as e:
                logger.error(
                    f"Generic error during Playwright fetch in WebClipper._fetch_content for {url}: {e}"
                )
                return None
        else:
            logger.info(f"Fetching {url} with aiohttp via WebClipper._fetch_content")
            try:
                async with aiohttp.ClientSession(
                    headers={"User-Agent": USER_AGENT}
                ) as session:
                    async with async_timeout.timeout(30):
                        async with session.get(url) as response:
                            if (
                                response.status == 200
                                and "text/html"
                                in response.headers.get("Content-Type", "")
                            ):
                                html_content = await response.text()
                            else:
                                logger.error(
                                    f"aiohttp failed to fetch {url} in WebClipper: status {response.status}"
                                )
                                return None
            except aiohttp.ClientError as e:
                logger.error(
                    f"aiohttp client error in WebClipper._fetch_content for {url}: {e}"
                )
                return None
            except asyncio.TimeoutError:
                logger.error(f"aiohttp timeout in WebClipper._fetch_content for {url}")
                return None
            except Exception as e:
                logger.error(
                    f"Generic error during aiohttp fetch in WebClipper._fetch_content for {url}: {e}"
                )
                return None

        if not html_content:
            return None

        soup = BeautifulSoup(html_content, "html.parser")
        title = (
            soup.title.string.strip()
            if soup.title and soup.title.string
            else url_to_filename(url)
        )
        return title, html_content

    def _generate_filename(self, title: str, timestamp: str) -> str:
        """Generate a clean filename from title and timestamp."""
        clean_title = "".join(c if c.isalnum() or c in "-_ " else "_" for c in title)
        clean_title = clean_title.replace(" ", "-")[:50]
        return f"{clean_title}-{timestamp}"

    async def clip(self, url: str, tags: Optional[List[str]] = None) -> dict:
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

                # Save markdown and PDF using FileManager for consistency
                md_info = self.file_manager.save_markdown(final_doc, timestamp, url)
                pdf_info = self.file_manager.save_pdf(final_doc, timestamp, url)

                return {
                    "title": "Aggregated content",
                    "url": url,
                    "markdown_path": md_info["relative_path"],
                    "pdf_path": pdf_info["relative_path"],
                    "timestamp": timestamp,
                    "status": "success",
                    "tags": tags or [],
                    "preview": (
                        final_doc[:500] + "..." if len(final_doc) > 500 else final_doc
                    ),
                }

            else:
                # Handle single URL
                fetch_result = await self._fetch_content(url)
                if not fetch_result:
                    logger.error(
                        f"Failed to fetch content for single URL: {url} in clip method"
                    )
                    # Return an error structure or raise an exception as appropriate
                    # For now, mimicking existing error return structure from clip method's main try-except
                    return {
                        "title": url_to_filename(url),
                        "url": url,
                        "status": "failed",
                        "error": f"Failed to fetch content for {url}",
                    }
                title, html_content = fetch_result
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

                # Extract and clean content (no heading prefix here)
                extracted_content = self.content_processor.extract_content(
                    html_content
                )  # Use html_content now
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

                # Save markdown and PDF via FileManager
                md_info = self.file_manager.save_markdown(final_doc, timestamp, url)
                pdf_info = self.file_manager.save_pdf(final_doc, timestamp, url)

                return {
                    "title": title,
                    "url": url,
                    "markdown_path": md_info["relative_path"],
                    "pdf_path": pdf_info["relative_path"],
                    "timestamp": timestamp,
                    "status": "success",
                    "tags": tags or [],
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
        sem = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

        async def fetch_html(u):
            if USE_PLAYWRIGHT_FOR_JS_CONTENT:
                logger.info(f"Fetching {u} with Playwright via WebClipper.process_urls")
                crawler = WebCrawler(base_url=u)  # Instantiate WebCrawler locally
                try:
                    html_text = await crawler.fetch_with_playwright(u)
                    if not html_text:
                        logger.warning(
                            f"Playwright fetch failed for {u} in process_urls, returning empty string."
                        )
                    return html_text or ""
                except PlaywrightError as e:
                    logger.error(f"Playwright error fetching {u} in process_urls: {e}")
                    return ""
                except asyncio.TimeoutError:
                    logger.error(f"Playwright timeout fetching {u} in process_urls")
                    return ""
                except Exception as e:
                    logger.error(
                        f"Generic Playwright error fetching {u} in process_urls: {e}"
                    )
                    return ""
            else:
                logger.info(f"Fetching {u} with aiohttp via WebClipper.process_urls")
                async with aiohttp.ClientSession(
                    headers={"User-Agent": USER_AGENT}
                ) as session:
                    async with sem:  # sem is defined in the outer scope of process_urls
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
                                        logger.warning(
                                            f"Invalid content at {u} (aiohttp): status {response.status}"
                                        )
                                        return ""
                        except aiohttp.ClientError as e:
                            logger.error(
                                f"aiohttp client error fetching {u} in process_urls: {e}"
                            )
                            return ""
                        except asyncio.TimeoutError:
                            logger.error(
                                f"Timeout fetching {u} with aiohttp in process_urls"
                            )
                            return ""
                        except Exception as e:
                            logger.error(
                                f"Generic error fetching {u} with aiohttp in process_urls: {e}"
                            )
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
