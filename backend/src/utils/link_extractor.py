# src/utils/link_extractor.py
import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class LinkExtractor:
    def extract_from_markdown(self, file_path: Path) -> dict:
        """Extract and organize links from a local markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if not content.strip():
                logger.warning(f"Empty content in file: {file_path}")
                return {}

            structure = {'Default': {'links': []}}
            current_section = 'Default'

            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.startswith('#'):
                    current_section = line.lstrip('#').strip()
                    if current_section not in structure:
                        structure[current_section] = {'links': []}
                    continue

                links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', line)
                for title, url in links:
                    structure[current_section]['links'].append({'title': title.strip(), 'url': url.strip()})

            return structure
        except Exception as e:
            logger.error(f"Error extracting links from markdown: {str(e)}")
            return {}

    def get_organized_links(self, structure: dict):
        links = []
        for section, content in structure.items():
            if 'links' in content:
                for link in content['links']:
                    if isinstance(link, dict) and 'title' in link and 'url' in link:
                        links.append((link['title'], link['url']))
        return links
