# config.py
import os

LOG_LEVEL = "INFO"
LOG_FILE = "aggregator.log"
USER_AGENT = "IntelligentAggregator/1.0"
MAX_CONCURRENT_REQUESTS = 5
NLP_MODEL = "en_core_web_lg"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
MARKETING_THRESHOLD = 0.6
USE_PLAYWRIGHT_FOR_JS_CONTENT = True  # Toggle for using Playwright for fetching

# Trafilatura settings
TRAFILATURA_INCLUDE_COMMENTS = False
TRAFILATURA_INCLUDE_TABLES = True

# JusText settings
JUSCONTENT_ENABLED = True  # Toggle for using JusText for cleaning
JUSCONTENT_DEFAULT_LANGUAGE = "English"
JUSCONTENT_LENGTH_LOW = 70  # Min length for a paragraph to be considered "good"
JUSCONTENT_STOPWORDS_HIGH = 0.30  # Max % of stopwords for a paragraph to be "good"
JUSCONTENT_MAX_LINK_DENSITY = 0.2  # Max ratio of link characters to total chars

# Markdownify settings
MARKDOWNIFY_HEADING_STYLE = "ATX"  # Use '#' for headings
MARKDOWNIFY_BULLET_STYLE = "*"      # Use '*' for bullet points
MARKDOWNIFY_STRIP_TAGS = ['script', 'style'] # Tags to strip from HTML
MARKDOWNIFY_CODE_LANGUAGE_CLASS = True # Infer code language from class names

DATA_DIR = "data"
INPUT_DIR = os.path.join(DATA_DIR, "inputs")
OUTPUT_DIR = os.path.join(DATA_DIR, "outputs")

if not os.path.exists(INPUT_DIR):
    os.makedirs(INPUT_DIR)
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

PDF_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "output.pdf")
MARKDOWN_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "output.md")

# WeasyPrint page setup configuration
WEASYPRINT_PAGE_SETUP = {
    'size': 'A4',
    'margin': '20mm'  # A single value applies to top, right, bottom, left
}
