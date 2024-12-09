# utils/helpers.py
import re
from urllib.parse import urljoin, urlparse

def is_absolute_url(url):
    return bool(urlparse(url).scheme)

def clean_text(text):
    # Basic cleanup - remove extra whitespace
    return re.sub(r'\s+', ' ', text).strip()

def guess_input_type(input_str):
    # Determine if input_str is:
    #   - a local sitemap file (check if file exists)
    #   - a URL to a sitemap.xml
    #   - a base URL for crawling
    # Assumption: If it's a URL and ends with 'sitemap.xml', it's a sitemap URL.
    # If it's a local file and ends with sitemap.xml, treat as local sitemap file.
    # Otherwise, treat as base URL.
    from os.path import isfile
    if isfile(input_str) and input_str.endswith("sitemap.xml"):
        return "local_sitemap_file"
    elif input_str.startswith("http") and input_str.endswith("sitemap.xml"):
        return "remote_sitemap"
    elif input_str.startswith("http"):
        return "base_url"
    else:
        # fallback - if it's not a file and not a URL, raise error
        raise ValueError("Invalid input. Provide a sitemap file, a sitemap URL, or a base URL.")
