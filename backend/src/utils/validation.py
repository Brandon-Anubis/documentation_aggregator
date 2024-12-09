# src/utils/validation.py
from urllib.parse import urlparse

class URLValidator:
    @staticmethod
    def is_valid_url(url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme in ['http', 'https'], result.netloc]) and len(url.strip()) < 2048
        except:
            return False
