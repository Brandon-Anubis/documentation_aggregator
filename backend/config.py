# config.py
import os

LOG_LEVEL = "INFO"
LOG_FILE = "aggregator.log"
USER_AGENT = "IntelligentAggregator/1.0"
MAX_CONCURRENT_REQUESTS = 5
NLP_MODEL = "en_core_web_lg"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
MARKETING_THRESHOLD = 0.6

DATA_DIR = "data"
INPUT_DIR = os.path.join(DATA_DIR, "inputs")
OUTPUT_DIR = os.path.join(DATA_DIR, "outputs")

if not os.path.exists(INPUT_DIR):
    os.makedirs(INPUT_DIR)
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

PDF_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "output.pdf")
MARKDOWN_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "output.md")

PDFKIT_OPTIONS = {
    'page-size': 'A4',
    'margin-top': '20mm',
    'margin-right': '20mm',
    'margin-bottom': '20mm',
    'margin-left': '20mm',
    'encoding': 'UTF-8',
    'no-outline': None,
    'enable-local-file-access': None
}
