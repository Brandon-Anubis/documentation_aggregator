# src/utils/content_cleaner.py
import logging
from typing import Optional
import lxml.html
import justext
from justext.utils import get_stoplist
from config import (
    JUSCONTENT_ENABLED,
    JUSCONTENT_DEFAULT_LANGUAGE,
    JUSCONTENT_LENGTH_LOW,
    JUSCONTENT_STOPWORDS_HIGH,
    JUSCONTENT_MAX_LINK_DENSITY,
)

logger = logging.getLogger(__name__)

class ContentCleaner:
    def __init__(self, config: Optional[dict] = None):
        self.config = config or {}
        # JusText parameters will be loaded from config in a subsequent step

    def clean_html_with_justext(self, html_content: str, language: str = JUSCONTENT_DEFAULT_LANGUAGE) -> str:
        """
        Cleans HTML content by removing boilerplate and non-content paragraphs using JusText.
        Outputs cleaned HTML.
        """
        if not JUSCONTENT_ENABLED:
            logger.info("JusText cleaning is disabled via config. Returning original HTML.")
            return html_content

        if not html_content or not isinstance(html_content, str):
            logger.warning("Empty or invalid HTML content received for JusText cleaning.")
            return html_content  # Return original if empty or invalid

        try:
            # Parse HTML with lxml
            dom = lxml.html.fromstring(html_content)

            # Get paragraphs classified by JusText.
            # Newer versions of jusText (>3.0) no longer accept the dom_root argument.
            paragraphs = list(
                justext.justext(
                    html_content,
                    get_stoplist(language),
                    length_low=JUSCONTENT_LENGTH_LOW,
                    stopwords_high=JUSCONTENT_STOPWORDS_HIGH,
                    max_link_density=JUSCONTENT_MAX_LINK_DENSITY,
                )
            )

            nodes_to_remove = []
            removed_paragraph_details_for_log = []
            logger.debug(f"JusText: Processing {len(paragraphs)} paragraphs from HTML content.")

            for i, p in enumerate(paragraphs):
                text_snippet = (p.text[:75] + '...') if len(p.text) > 75 else p.text
                # Detailed log for every paragraph processed by JusText
                logger.debug(
                    f"JusText classified paragraph {i+1}/{len(paragraphs)}: "
                    f"class='{p.class_type}', chars={len(p.text)}, "
                    f"stopwords_density={p.stopwords_density:.2f}, "
                    f"link_density={p.link_density:.2f}, "
                    f"final_class='{p.final_class}', " # Added final_class for more detail
                    f"text_snippet='{text_snippet.strip()}'"
                )

                if p.class_type == 'bad': # Or consider p.final_class == 'bad'
                    logger.info(
                        f"JusText: Marking paragraph {i+1} as '{p.class_type}' and queueing for removal. "
                        f"Snippet: '{text_snippet.strip()}'"
                    )
                    nodes_to_remove.extend(p.html_nodes)
                    removed_paragraph_details_for_log.append(
                        f"  - Para {i+1}: Class='{p.class_type}', FinalClass='{p.final_class}', Snippet: '{text_snippet.strip()}', "
                        f"Len: {p.length}, SW_Dens: {p.stopwords_density:.2f}, Link_Dens: {p.link_density:.2f}"
                    )
            
            if removed_paragraph_details_for_log:
                logger.info(f"JusText: Summary of removed 'bad' paragraphs ({len(removed_paragraph_details_for_log)} total):")
                for detail in removed_paragraph_details_for_log:
                    logger.info(detail)
            else:
                logger.info("JusText: No paragraphs classified as 'bad' were marked for removal.")
            
            # Remove identified 'bad' nodes from the DOM
            # Iterate in reverse document order or collect and remove to avoid issues while modifying the tree
            # For simplicity here, we collect and then remove. Lxml handles removal robustly.
            for node in set(nodes_to_remove): # Use set to avoid issues if nodes are duplicated
                parent = node.getparent()
                if parent is not None:
                    try:
                        parent.remove(node)
                    except Exception as e:
                        logger.warning(f"JusText: Could not remove node {node.tag} (path: {node.getroottree().getpath(node)}): {e}")

            # Serialize the modified DOM back to HTML
            cleaned_html = lxml.html.tostring(dom, encoding='unicode')
            
            # Check if cleaning resulted in empty content (e.g. if everything was 'bad')
            # In such a case, it might be better to return the original HTML or a specific marker.
            # For now, return the (potentially empty) cleaned_html.
            if not cleaned_html.strip() or cleaned_html.lower() == "<html><body></body></html>":
                 logger.warning("JusText cleaning resulted in empty HTML. Original HTML might have been all boilerplate.")
                 # Potentially return original html_content here if preferred over empty

            return cleaned_html

        except lxml.etree.ParserError as e:
            logger.error(f"LXML parsing error during JusText cleaning: {e}. Returning original HTML.")
            return html_content # Fallback to original HTML on parsing error
        except Exception as e:
            logger.error(f"Error during JusText cleaning: {e}. Returning original HTML.", exc_info=True)
            return html_content # Fallback to original HTML on other errors
