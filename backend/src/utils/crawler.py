# src/utils/crawler.py
import asyncio
import aiohttp
import async_timeout
import logging
import random
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from bs4 import BeautifulSoup
from config import USER_AGENT, MAX_CONCURRENT_REQUESTS

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
                    logger.info(f"Skipping {url} due to robots.txt rules.")
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
        except Exception as e:
            logger.warning(f"No valid robots.txt fetched: {e}")

    async def fetch_page(self, session, url):
        async with self.sem:
            try:
                async with async_timeout.timeout(10):
                    async with session.get(url) as resp:
                        if resp.status == 200 and 'text/html' in resp.headers.get('Content-Type', ''):
                            return await resp.text()
                        return None
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
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
