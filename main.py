# main.py
import sys
import logging
from src.web_clipper import WebClipper
from config import LOG_LEVEL, LOG_FILE

logging.basicConfig(level=LOG_LEVEL, filename=LOG_FILE,
                    format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <input>")
        sys.exit(1)

    input_str = sys.argv[1]
    clipper = WebClipper()
    result = clipper.clip(input_str)
    if result:
        print(f"Documentation successfully aggregated to {result}")
    else:
        print("No documentation could be aggregated. Check logs for details.")

if __name__ == "__main__":
    main()








# # main.py
# import asyncio
# import sys
# from typing import List, Tuple
# from src.utils.logger import logger
# from src.utils.helpers import guess_input_type
# from src.crawler.sitemap import parse_sitemap
# from src.crawler.crawler import WebCrawler
# from src.analysis.cleaning import clean_html_content
# from src.analysis.nlp import NLPProcessor
# from src.analysis.embeddings import EmbeddingGenerator
# from src.aggregation.aggregator import ContentAggregator
# from src.aggregation.toc import TOCGenerator
# from src.output.markdown import MarkdownOutput
# from src.output.pdf_generator import PDFOutput
# from config import MARKDOWN_OUTPUT_FILE, PDF_OUTPUT_FILE

# async def main():
#     if len(sys.argv) < 2:
#         print("Usage: python main.py <input>")
#         sys.exit(1)

#     input_str = sys.argv[1]
#     input_type = guess_input_type(input_str)

#     if input_type == "local_sitemap_file":
#         urls = parse_sitemap(input_str, is_file=True)
#         pages_raw = await fetch_pages(urls)
#     elif input_type == "remote_sitemap":
#         urls = parse_sitemap(input_str, is_file=False)
#         pages_raw = await fetch_pages(urls)
#     else:  # base_url
#         crawler = WebCrawler(input_str)
#         pages_raw = await crawler.run(max_pages=50)

#     if not pages_raw:
#         logger.warning("No pages found or fetched. Exiting.")
#         print("No pages were retrieved. Please check your input.")
#         return

#     nlp = NLPProcessor()

#     def cleaned_text_sections(url, content):
#         import re
#         # We'll assume content has markdown headings now. If not, adapt as needed.
#         sections = re.split(r'(^#{1,6}\s.*)$', content, flags=re.M)
#         results = []
#         current_title = None
#         current_content = []
#         for part in sections:
#             if re.match(r'^#{1,6}\s', part or ''):
#                 if current_title or current_content:
#                     results.append({"url": url, "title": current_title, "content": '\n'.join(current_content)})
#                     current_content = []
#                 current_title = part.strip()
#             else:
#                 if part.strip():
#                     current_content.append(part.strip())
#         if current_title or current_content:
#             results.append({"url": url, "title": current_title, "content": '\n'.join(current_content)})
#         return results

#     cleaned_pages = []
#     for url, html in pages_raw:
#         cleaned = clean_html_content(html)
#         if nlp.classify_relevance(cleaned):
#             sectioned = cleaned_text_sections(url, cleaned)
#             cleaned_pages.append((url, sectioned))

#     # Remove repetitive trailing paragraphs
#     cleaned_pages = remove_repetitive_trailing_paragraphs(cleaned_pages, threshold=0.8)

#     if not cleaned_pages:
#         logger.warning("No relevant pages after NLP filtering and removal of duplicates. Exiting.")
#         print("No relevant pages were found after filtering. Check the relevance criteria.")
#         return

#     # Flatten all sections from all pages
#     all_sections = []
#     for url, sections in cleaned_pages:
#         all_sections.extend(sections)

#     embedder = EmbeddingGenerator()
#     section_texts = [s['content'] for s in all_sections]
#     if section_texts:
#         embeddings = embedder.generate_embeddings(section_texts)
#         for i, emb in enumerate(embeddings):
#             all_sections[i]['embedding'] = emb

#     aggregator = ContentAggregator()
#     combined_content = []
#     for s in all_sections:
#         if s['title']:
#             combined_content.append(s['title'])
#         combined_content.append(s['content'])
#     aggregated = "\n\n".join(combined_content)

#     toc_gen = TOCGenerator()
#     toc = toc_gen.generate_toc(aggregated)

#     md_writer = MarkdownOutput()
#     md_file = md_writer.write(toc, aggregated)
#     logger.info(f"Markdown output written to {md_file}")

#     pdf_writer = PDFOutput()
#     pdf_file = pdf_writer.write(aggregated)
#     logger.info(f"PDF output written to {pdf_file}")

#     # Summaries if needed
#     summaries = {}
#     for s in all_sections:
#         if s['title'] and s['title'].startswith('# '):
#             summaries[s['title']] = s['content'][:200] + "..."

#     print("Aggregation and compilation complete.")

# def remove_repetitive_trailing_paragraphs(cleaned_pages, threshold=0.8):
#     last_paragraphs = []
#     for _, sections in cleaned_pages:
#         if sections:
#             last_section_content = sections[-1]['content'].strip()
#             paragraphs = [p.strip() for p in last_section_content.split('\n\n') if p.strip()]
#             if paragraphs:
#                 last_paragraphs.append(paragraphs[-1])

#     if not last_paragraphs:
#         return cleaned_pages

#     from collections import Counter
#     counts = Counter(last_paragraphs)
#     total = len(last_paragraphs)
#     repetitive = [p for p, c in counts.items() if (c / total) > threshold]

#     if not repetitive:
#         return cleaned_pages

#     new_cleaned_pages = []
#     for url, sections in cleaned_pages:
#         new_sections = []
#         for s in sections:
#             paragraphs = [p.strip() for p in s['content'].split('\n\n') if p.strip()]
#             paragraphs = [p for p in paragraphs if p not in repetitive]
#             s['content'] = '\n\n'.join(paragraphs).strip()
#             new_sections.append(s)
#         new_cleaned_pages.append((url, new_sections))
#     return new_cleaned_pages

# async def fetch_pages(urls):
#     from aiohttp import ClientSession
#     import async_timeout
#     pages = []
#     async with ClientSession() as session:
#         for u in urls:
#             try:
#                 async with async_timeout.timeout(10):
#                     async with session.get(u) as resp:
#                         if resp.status == 200 and 'text/html' in resp.headers.get('Content-Type', ''):
#                             html = await resp.text()
#                             pages.append((u, html))
#             except Exception as e:
#                 logger.error(f"Error fetching {u}: {e}")
#     return pages

# if __name__ == "__main__":
#     asyncio.run(main())
