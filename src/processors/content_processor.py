# src/processors/content_processor.py
import logging
import html2text
import bleach
from readability import Document
import re
from typing import List
from src.utils.content_cleaner import ContentCleaner
from src.utils.deduplication import SemanticContentCleaner
from config import EMBEDDING_MODEL

logger = logging.getLogger(__name__)

def post_process_markdown(content: str) -> str:
    lines = content.split('\n')
    processed_lines = []
    in_code_block = False

    for line in lines:
        if line.strip().startswith('```'):
            in_code_block = not in_code_block
            processed_lines.append(line)
            continue
        if in_code_block:
            processed_lines.append(line)
            continue

        line = re.sub(r'\s+', ' ', line).strip()
        if line:
            processed_lines.append(line)

    content = '\n'.join(processed_lines)
    content = re.sub(r'\n{3,}', '\n\n', content)
    return content

class ContentProcessor:
    def __init__(self):
        self.markdown_converter = html2text.HTML2Text()
        self.markdown_converter.ignore_images = False
        self.markdown_converter.ignore_links = False
        self.markdown_converter.body_width = 0
        self.markdown_converter.unicode_snob = True
        self.markdown_converter.protect_links = True
        self.markdown_converter.wrap_links = False
        self.markdown_converter.bypass_tables = False

        self.allowed_tags = list(bleach.sanitizer.ALLOWED_TAGS) + [
            'p', 'pre', 'code', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'img', 'table', 'tr', 'td', 'th', 'thead', 'tbody',
            'ul', 'ol', 'li', 'strong', 'em', 'blockquote', 'a',
            'div', 'span', 'math'
        ]
        self.allowed_attributes = dict(bleach.sanitizer.ALLOWED_ATTRIBUTES)
        self.allowed_attributes.update({
            '*': ['class', 'id', 'name', 'data-*'],
            'img': ['src', 'alt', 'title'],
            'a': ['href', 'title'],
            'pre': ['class', 'data-language'],
            'code': ['class', 'data-language']
        })

        self.content_cleaner = ContentCleaner()
        self.semantic_cleaner = SemanticContentCleaner(EMBEDDING_MODEL)

    def extract_content(self, html: str) -> str:
        try:
            if not html.strip():
                logger.warning("Empty HTML content received")
                return ""

            doc = Document(html)
            content_html = doc.summary()
            if not content_html:
                logger.warning("No content extracted by readability")
                return ""

            sanitized_html = bleach.clean(
                content_html,
                tags=self.allowed_tags,
                attributes=self.allowed_attributes,
                strip=True
            )

            if not sanitized_html.strip():
                logger.warning("Content was empty after sanitization")
                return ""

            markdown_content = self.markdown_converter.handle(sanitized_html)
            processed_content = post_process_markdown(markdown_content)

            # Remove marketing sections and refine content via NLP
            processed_content = self.content_cleaner.clean_content(processed_content)
            return processed_content
        except Exception as e:
            logger.error(f"Error extracting content: {str(e)}", exc_info=True)
            return ""

    def generate_markdown(self, content_list: List[dict], timestamp: str, include_meta: bool = True) -> str:
        if not content_list:
            logger.warning("Empty content list received")
            return ""

        # Semantic deduplication
        content_list = self.semantic_cleaner.remove_semantic_duplicates(content_list)

        output = []
        output.append("# Clipped Content\n")
        if include_meta:
            output.append(f"*Generated: {timestamp}*\n")
        output.append("---\n")

        for item in content_list:
            title = item.get('title', 'Untitled')
            url = item.get('url', '')
            content = item.get('content', '').strip()

            output.append(f"\n## {title}\n")
            if include_meta and url:
                output.append(f"*Source: [{url}]({url})*\n")

            if content:
                output.append("\n" + content + "\n")
            else:
                output.append("\n*No content could be extracted from this page.*\n")

            output.append("\n---\n")

        return '\n'.join(output)
