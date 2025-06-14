# src/utils/crawler.py
import asyncio
import aiohttp
import async_timeout
import logging
import random
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Error as PlaywrightError
from config import USER_AGENT, MAX_CONCURRENT_REQUESTS, USE_PLAYWRIGHT_FOR_JS_CONTENT

logger = logging.getLogger(__name__)

class WebCrawler:
    def __init__(self, base_url: str, max_pages=100, delay=1.0):
        self.base_url = base_url
        self.visited = set()
        self.to_visit = asyncio.Queue()
        self.sem = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        self.max_pages = max_pages
        self.delay = delay
        self.robot_parser = RobotFileParser()
        self.robot_parser.set_url(urljoin(self.base_url, "/robots.txt"))

    async def run(self):
        # Fetch robots.txt
        await self._fetch_robots_txt()
        await self.to_visit.put(self.base_url)
        pages = []
        async with aiohttp.ClientSession(headers={"User-Agent": USER_AGENT}) as session:
            while not self.to_visit.empty() and len(pages) < self.max_pages:
                url = await self.to_visit.get()
                if url in self.visited:
                    continue
                if not self.robot_parser.can_fetch(USER_AGENT, url):
                    logger.info("Skipping %s due to robots.txt rules.", url)
                    continue
                self.visited.add(url)
                await asyncio.sleep(self.delay + random.uniform(0, 0.5))
                content = await self.fetch_page(session, url)
                if content:
                    pages.append(url)
                    for link in self.extract_links(url, content):
                        if link not in self.visited:
                            await self.to_visit.put(link)
        return pages
    
    async def _fetch_robots_txt(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(urljoin(self.base_url, "robots.txt")) as resp:
                    if resp.status == 200:
                        robots_content = await resp.text()
                        self.robot_parser.parse(robots_content.split('\n'))
        except aiohttp.ClientError as e: # More specific exception
            logger.warning("No valid robots.txt fetched (aiohttp error): %s", e)
        except Exception as e: # Catch other potential errors
            logger.warning("No valid robots.txt fetched (general error): %s", e)

    async def fetch_page(self, session, url: str):
        if USE_PLAYWRIGHT_FOR_JS_CONTENT:
            # Note: The original fetch_page took 'session' as an argument from aiohttp.ClientSession
            # fetch_with_playwright manages its own browser session.
            # If aiohttp session is crucial here for some reason, this logic might need adjustment.
            content = await self.fetch_with_playwright(url)
            if content:
                return content
            # Fallback to aiohttp if Playwright fails (optional, as fetch_with_playwright logs its own errors)
            # For now, if Playwright is enabled and fails, we return None as per fetch_with_playwright's behavior.
            # If a more explicit fallback to aiohttp on Playwright failure is desired, that logic would go here.
            logger.info("Playwright fetching enabled but failed for %s, not falling back to aiohttp in this path.", url)
            return None
        else:
            logger.info("Fetching %s with aiohttp", url)
            async with self.sem:
                try:
                    async with async_timeout.timeout(10):
                        async with session.get(url) as resp:
                            if resp.status == 200 and 'text/html' in resp.headers.get('Content-Type', ''):
                                return await resp.text()
                            logger.warning("aiohttp fetch for %s failed with status %s", url, resp.status)
                            return None
                except aiohttp.ClientError as e:
                    logger.error("Error fetching %s with aiohttp: %s", url, e)
                    return None
                except asyncio.TimeoutError:
                    logger.error("Timeout fetching %s with aiohttp", url)
                    return None
                except Exception as e: # Catch other potential errors during aiohttp fetch
                    logger.error("Generic error fetching %s with aiohttp: %s", url, e)
                    return None

    async def fetch_with_playwright(self, url: str):
        async with self.sem: # Reuse existing semaphore for concurrency control
            logger.info("Fetching %s with Playwright", url)
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch()
                    page = await browser.new_page()
                    await page.goto(url, wait_until='networkidle', timeout=30000) # Wait for network to be idle, timeout 30s
                    content = await page.content()
                    await browser.close()
                    return content
            except PlaywrightError as e: # More specific Playwright exception
                logger.error("Error fetching %s with Playwright: %s", url, e)
                return None
            except asyncio.TimeoutError:
                logger.error("Timeout fetching %s with Playwright", url)
                return None
            except Exception as e: # Catch other potential errors during Playwright fetch
                logger.error("Generic error fetching %s with Playwright: %s", url, e)
                return None

    def extract_links(self, base_url, html):
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        domain = urlparse(self.base_url).netloc
        for a in soup.select('a[href]'):
            href = str(a.get('href', ''))
            full_url = urljoin(base_url, href)
            if urlparse(full_url).netloc == domain:
                links.append(full_url)
        return links
