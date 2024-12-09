# src/utils/content_cleaner.py
import re
import logging
from typing import List, Optional
from src.utils.marketing_detector import MarketingContentDetector

logger = logging.getLogger(__name__)

class ContentCleaner:
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        self.marketing_detector = MarketingContentDetector()
        
    def clean_content(self, markdown_content: str) -> str:
        if not markdown_content or not isinstance(markdown_content, str):
            return ""

        sections = self._split_into_sections(markdown_content)
        if not sections:
            return ""

        clean_sections = []
        for i, section in enumerate(sections):
            if not section.strip():
                continue

            if not self._is_marketing_section(section, context=sections, position=i):
                clean_sections.append(section)

        if not clean_sections:
            return markdown_content

        return "\n\n".join(clean_sections)
    
    def _split_into_sections(self, content: str) -> List[str]:
        """Split content into logical sections"""
        # First try splitting by headers
        sections = re.split(r'\n##?\s+', content)
        
        # If no headers found, try splitting by paragraphs
        if len(sections) <= 1:
            sections = [s.strip() for s in content.split('\n\n') if s.strip()]
        
        return sections
    
    def _is_marketing_section(self, section: str, context: List[str], position: int) -> bool:
        """Determine if a section is marketing content with context awareness"""
        if not section.strip():
            return False

        try:
            is_marketing = self.marketing_detector.is_marketing_section(section)

            # If it's the last section, also check additional indicators
            if position == len(context) - 1:
                return is_marketing or self._has_marketing_indicators(section)

            return is_marketing
        except Exception as e:
            logger.warning(f"Error in _is_marketing_section: {e}")
            return False
    
    def _has_marketing_indicators(self, section: str) -> bool:
        """Check for additional marketing indicators"""
        doc = self.marketing_detector.nlp(section)
        return any([
            doc._.marketing_score > 0.4,
            len([ent for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT"]]) > 0,
            any(token.like_url for token in doc)
        ])
