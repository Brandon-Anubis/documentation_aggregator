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

        self.output_format = self.config.get("output_format", "markdown")
        self.include_metadata = self.config.get("include_metadata", True)

    async def process_urls(self, urls: list) -> list:
        results = []
        from config import USER_AGENT, MAX_CONCURRENT_REQUESTS
        import aiohttp, async_timeout

        sem = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

        async def fetch_html(url):
            async with aiohttp.ClientSession(
                headers={"User-Agent": USER_AGENT}
            ) as session:
                async with sem:
                    try:
                        async with async_timeout.timeout(30):
                            async with session.get(url) as response:
                                if (
                                    response.status == 200
                                    and "text/html"
                                    in response.headers.get("Content-Type", "")
                                ):
                                    return await response.text()
                                else:
                                    logger.warning(
                                        f"Invalid content type or status at {url}"
                                    )
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
            return {"url": url, "title": title or url, "content": content}

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
        async def run():
            urls = await self.input_handler.fetch_urls(input_str)
            if not urls:
                logger.error("No URLs found from input.")
                return None
            logger.info(f"Processing {len(urls)} URLs")
            content_list = await self.process_urls(urls)
            logger.info(
                f"Successfully processed {len(content_list)} URLs out of {len(urls)}"
            )
            if not content_list:
                logger.error("No content was successfully aggregated")
                return None

            timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
            final_markdown = self.content_processor.generate_markdown(
                content_list, timestamp, self.include_metadata
            )

            # Use the first URL directly without any type checking
            url = urls[0] if isinstance(urls[0], str) else urls[0][1]

            if self.output_format == "markdown":
                return self.file_manager.save_markdown(final_markdown, timestamp, url)
            elif self.output_format == "pdf":
                return self.file_manager.save_pdf(final_markdown, timestamp, url)
            else:
                logger.error(f"Unknown output format: {self.output_format}")
                return None

        return run()
