# utils/helpers.py
import re
from urllib.parse import urljoin, urlparse


def is_absolute_url(url):
    return bool(urlparse(url).scheme)


def clean_text(text):
    # Basic cleanup - remove extra whitespace
    return re.sub(r"\s+", " ", text).strip()


def guess_input_type(input_str):
    from os.path import isfile

    if isfile(input_str) and input_str.endswith("sitemap.xml"):
        return "local_sitemap_file"
    elif input_str.startswith("http") and input_str.endswith("sitemap.xml"):
        return "remote_sitemap"
    elif input_str.startswith("http"):
        return "base_url"
    else:
        # fallback - if it's not a file and not a URL, raise error
        raise ValueError(
            "Invalid input. Provide a sitemap file, a sitemap URL, or a base URL."
        )


def url_to_filename(url: str) -> str:
    """Convert a URL to a safe filename using just the domain."""
    # Parse the URL
    parsed = urlparse(url)

    # Get the domain (without www.)
    domain = parsed.netloc.replace("www.", "")

    # Replace any remaining dots with hyphens
    return domain.replace(".", "-")
