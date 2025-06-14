# src/utils/sitemap_parser.py
import logging
import aiohttp
import asyncio  # Added for asyncio.TimeoutError
import async_timeout
from bs4 import BeautifulSoup
import os  # Keep os import

logger = logging.getLogger(__name__)


class SitemapParser:
    async def parse_sitemap_url(self, sitemap_url: str) -> list:
        """Fetch and parse a remote sitemap.xml URL."""
        try:
            async with aiohttp.ClientSession() as session:
                async with async_timeout.timeout(30):  # Timeout for the request
                    async with session.get(sitemap_url) as resp:
                        if resp.status == 200:
                            text = await resp.text()
                            if not text:
                                logger.warning("Sitemap at %s is empty.", sitemap_url)
                                return []
                            # Pass sitemap_url as source_identifier
                            return self.parse_sitemap_content(
                                text, source_identifier=sitemap_url
                            )
                        else:
                            logger.warning(
                                "Failed to fetch sitemap from %s, status %s",
                                sitemap_url,
                                resp.status,
                            )
                            return []
        except asyncio.TimeoutError:  # More specific exception
            logger.error("Timeout fetching sitemap %s", sitemap_url)
            return []
        except aiohttp.ClientError as e:  # More specific exception
            logger.error("aiohttp.ClientError fetching sitemap %s: %s", sitemap_url, e)
            return []
        except Exception as e:
            logger.error(
                "Generic error parsing remote sitemap %s: %s",
                sitemap_url,
                e,
                exc_info=True,
            )
            return []

    def parse_sitemap_file(self, file_path: str) -> list:
        """Parse a local sitemap.xml file."""
        if not os.path.exists(file_path):  # Good check
            logger.error("Sitemap file not found: %s", file_path)
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                if not content:
                    logger.warning("Local sitemap file %s is empty.", file_path)
                    return []
                # Pass file_path as source_identifier
                return self.parse_sitemap_content(content, source_identifier=file_path)
        except (
            FileNotFoundError
        ):  # Already handled by os.path.exists, but good for clarity
            logger.error("Sitemap file not found (redundant check): %s", file_path)
            return []
        except Exception as e:
            # Corrected variable name from 'filepath' to 'file_path' in log
            logger.error(
                "Error parsing local sitemap file %s: %s", file_path, e, exc_info=True
            )
            return []

    def parse_sitemap_content(
        self, content: str, source_identifier: str = "sitemap"
    ) -> list:
        """
        Parse sitemap XML content.
        source_identifier is the URL or filepath for logging purposes.
        """
        try:
            # Using 'lxml-xml' for robustness with XML.
            soup = BeautifulSoup(content, "lxml-xml")

            # Check for sitemap index files (tags like <sitemapindex><sitemap><loc>...</loc></sitemap>...)
            # A sitemap index file typically has a <sitemapindex> root or <sitemap> tags without <url> tags.
            is_sitemap_index = soup.find("sitemapindex") or (
                soup.find_all("sitemap") and not soup.find_all("url")
            )

            if is_sitemap_index:
                logger.info("Sitemap index file detected for %s.", source_identifier)
                # Extract URLs from <sitemap><loc>...</loc></sitemap>
                # Ensure loc_tag itself is not None before calling get_text
                urls = [
                    loc_tag.get_text(strip=True)
                    for sitemap_tag in soup.find_all("sitemap")
                    for loc_tag in sitemap_tag.find_all("loc")
                    if loc_tag and loc_tag.get_text(strip=True)
                ]
                if not urls:
                    logger.warning(
                        "Sitemap index file %s found, but no <loc> tags with content within <sitemap> tags, or sitemap tags are empty.",
                        source_identifier,
                    )
                else:
                    logger.info(
                        "Extracted %s sitemap URLs from index %s.",
                        len(urls),
                        source_identifier,
                    )
                # NOTE: This does not recursively parse these sitemap URLs yet.
                return urls

            # Standard sitemap parsing for <url><loc>...</loc></url>
            url_entries = soup.find_all("url")
            if not url_entries:
                # Fallback: if no <url> tags, perhaps it's a simpler sitemap with just <loc> tags directly under root.
                direct_loc_tags = soup.find_all("loc")
                if not direct_loc_tags:
                    logger.warning(
                        "No <url> tags or direct <loc> tags found in sitemap content from %s.",
                        source_identifier,
                    )
                    return []

                logger.info(
                    "No <url> tags found in %s, directly extracting from %s <loc> tags.",
                    source_identifier,
                    len(direct_loc_tags),
                )
                # Ensure loc_tag itself is not None before calling get_text
                valid_direct_locs = [
                    loc_tag.get_text(strip=True)
                    for loc_tag in direct_loc_tags
                    if loc_tag and loc_tag.get_text(strip=True)
                ]
                if not valid_direct_locs:
                    logger.warning(
                        "Found direct <loc> tags in %s, but they are all empty or contain no text.",
                        source_identifier,
                    )
                return valid_direct_locs

            # Extract <loc> from within each <url>
            extracted_urls = []
            for url_tag in url_entries:
                loc_tag = url_tag.find("loc")
                if loc_tag and loc_tag.get_text(
                    strip=True
                ):  # Ensure loc_tag exists and has text
                    extracted_urls.append(loc_tag.get_text(strip=True))

            if not extracted_urls:
                logger.warning(
                    "Found %s <url> tags in %s, but no valid <loc> tags with content within them or <loc> tags are empty.",
                    len(url_entries),
                    source_identifier,
                )
            else:
                logger.info(
                    "Extracted %s content URLs from %s.",
                    len(extracted_urls),
                    source_identifier,
                )
            return extracted_urls

        except Exception as e:
            # This will catch errors from BeautifulSoup parsing (e.g., if lxml raises an error on malformed XML)
            logger.error(
                "Critical error parsing sitemap XML content from %s: %s",
                source_identifier,
                e,
                exc_info=True,
            )
            return []
