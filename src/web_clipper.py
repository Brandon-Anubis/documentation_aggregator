# src/web_clipper.py
import asyncio
import logging
from datetime import datetime
from typing import Optional
from src.processors.content_processor import ContentProcessor
from src.utils.file_manager import FileManager
from src.utils.input_handler import InputHandler

logger = logging.getLogger(__name__)

class WebClipper:
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.file_manager = FileManager()
        self.content_processor = ContentProcessor()
        self.input_handler = InputHandler(self.file_manager)

        self.output_format = self.config.get('output_format', 'markdown')
        self.include_metadata = self.config.get('include_metadata', True)

    async def process_urls(self, urls: list) -> list:
        # For each URL in urls, fetch content
        # We already have an async fetch logic integrated into content_processor?
        # content_processor handles HTML once fetched by web_clipper
        # Wait, we need a fetch_html here?
        # Actually, content_processor expects HTML from extract_content calls by us.
        # Let's just fetch HTML here (like previously) using fetch_html from web_clipper or from earlier logic.

        # We'll reuse the logic: Since previously we had fetch_html and fetch_content_from_url integrated,
        # we need that logic back here. We'll write a small fetch_html & fetch_content_from_url inside web_clipper.
        results = []
        from config import USER_AGENT, MAX_CONCURRENT_REQUESTS
        import aiohttp, async_timeout
        sem = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

        async def fetch_html(url):
            async with aiohttp.ClientSession(headers={"User-Agent": USER_AGENT}) as session:
                async with sem:
                    try:
                        async with async_timeout.timeout(30):
                            async with session.get(url) as response:
                                if response.status == 200 and 'text/html' in response.headers.get('Content-Type', ''):
                                    return await response.text()
                                else:
                                    logger.warning(f"Invalid content type or status at {url}")
                                    return ""
                    except Exception as e:
                        logger.error(f"Error fetching {url}: {e}")
                        return ""

        async def process_url(title_url):
            title, url = title_url if isinstance(title_url, tuple) else ("", title_url)
            html = await fetch_html(url)
            if not html:
                return None
            content = self.content_processor.extract_content(html)
            if not content:
                return None
            return {
                'url': url,
                'title': title or url,
                'content': content
            }

        tasks = [process_url(u) for u in urls]
        processed_count = 0
        res = await asyncio.gather(*tasks, return_exceptions=True)
        valid_results = []
        for r in res:
            processed_count += 1
            if isinstance(r, Exception):
                logger.error(f"Error processing URL: {str(r)}")
            elif r is not None:
                valid_results.append(r)
            logger.info(f"Processed {processed_count}/{len(urls)} URLs")
        return valid_results

    def clip(self, input_str: str) -> Optional[str]:
        # We now handle all input types through input_handler
        # input_handler returns either a list of urls as strings or a list of (title, url) tuples for markdown

        async def run():
            urls = await self.input_handler.fetch_urls(input_str)
            if not urls:
                logger.error("No URLs found from input.")
                return None
            logger.info(f"Processing {len(urls)} URLs")
            content_list = await self.process_urls(urls)
            logger.info(f"Successfully processed {len(content_list)} URLs out of {len(urls)}")
            if not content_list:
                logger.error("No content was successfully aggregated")
                return None

            timestamp = datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')
            final_markdown = self.content_processor.generate_markdown(content_list, timestamp, self.include_metadata)

            if self.output_format == 'markdown':
                return self.file_manager.save_markdown(final_markdown, timestamp)
            elif self.output_format == 'pdf':
                return self.file_manager.save_pdf(final_markdown, timestamp)
            else:
                logger.error(f"Unknown output format: {self.output_format}")
                return None

        return asyncio.run(run())
