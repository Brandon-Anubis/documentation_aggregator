# src/exceptions.py
class WebClipperError(Exception):
    """Base exception for web clipper"""
    pass

class URLValidationError(WebClipperError):
    """Raised when URL validation fails"""
    pass

class ContentFetchError(WebClipperError):
    """Raised when content cannot be fetched"""
    pass

class OutputGenerationError(WebClipperError):
    """Raised when output generation fails"""
    pass

class FileProcessingError(WebClipperError):
    """Raised when file processing fails"""
    pass
