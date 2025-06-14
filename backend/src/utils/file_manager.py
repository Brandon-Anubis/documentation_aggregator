# src/utils/file_manager.py
import os
import markdown
import logging
from pathlib import Path
from src.utils.helpers import url_to_filename
from config import OUTPUT_DIR, INPUT_DIR, WEASYPRINT_PAGE_SETUP

logger = logging.getLogger(__name__)

# Try to use xhtml2pdf for cross-platform PDF generation; fall back to minimal placeholder.
try:
    from xhtml2pdf import pisa  # type: ignore
    _PDF_ENGINE = "xhtml2pdf"
except ImportError:
    pisa = None  # type: ignore
    _PDF_ENGINE = "placeholder"


class FileManager:
    def __init__(self):
        self.INPUT_DIR = Path(INPUT_DIR)
        self.OUTPUT_DIR = Path(OUTPUT_DIR)
        self.MARKDOWN_OUTPUT_DIR = self.OUTPUT_DIR / "markdown"
        self.PDF_OUTPUT_DIR = self.OUTPUT_DIR / "pdf"
        self.initialize_directories()

    def initialize_directories(self):
        for directory in [self.MARKDOWN_OUTPUT_DIR, self.PDF_OUTPUT_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

    def get_input_path(self, filename: str) -> Path:
        return self.INPUT_DIR / filename

    def _generate_filepath(self, base_name: str, timestamp: str, extension: str) -> str:
        """Generate a filepath with website name and timestamp."""
        # Remove any path separators and use only the domain part
        safe_name = base_name.replace("/", "-")
        return f"{safe_name}-{timestamp}.{extension}"

    def save_markdown(self, content: str, timestamp: str, url: str = None) -> dict:
        try:
            if url:
                base_name = url_to_filename(url)
                filename = self._generate_filepath(base_name, timestamp, "md")
            else:
                filename = f"clipped_{timestamp}.md"

            output_path = self.MARKDOWN_OUTPUT_DIR / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            return {
                "full_path": str(output_path),
                "relative_path": str(output_path.relative_to(self.OUTPUT_DIR)),
            }
        except Exception as e:
            logger.error(f"Error saving markdown: {e}")
            return {"full_path": "", "relative_path": ""}

    def save_pdf(self, markdown_content: str, timestamp: str, url: str = None) -> dict:
        try:
            if url:
                base_name = url_to_filename(url)
                filename = self._generate_filepath(base_name, timestamp, "pdf")
            else:
                filename = f"clipped_{timestamp}.pdf"

            output_path = self.PDF_OUTPUT_DIR / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)

            html_content = self._create_styled_html(markdown_content)

            if _PDF_ENGINE == "xhtml2pdf" and pisa is not None:
                with open(output_path, "wb") as pdf_file:
                    pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
                    if pisa_status.err:
                        raise RuntimeError("xhtml2pdf failed to generate PDF")
            else:
                raise RuntimeError("No PDF engine available, falling back to placeholder")
            return {
                "full_path": str(output_path),
                "relative_path": str(output_path.relative_to(self.OUTPUT_DIR)),
            }
        except Exception as e:
            logger.error(f"Error saving PDF: {e}", exc_info=True)
            # Graceful degradation: create an empty placeholder PDF so downstream logic doesn't break
            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                # Create 0-byte or minimal PDF placeholder
                with open(output_path, "wb") as f:
                    # Write minimal PDF header/footer to make it a valid file
                    f.write(b"%PDF-1.4\n%%\xe2\xe3\xcf\xd3\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF")
            except Exception as write_err:
                logger.error("Failed to create placeholder PDF: %s", write_err)
            return {
                "full_path": str(output_path),
                "relative_path": str(output_path.relative_to(self.OUTPUT_DIR)),
            }

    def _create_styled_html(self, markdown_content: str) -> str:
        html_content = markdown.markdown(
            markdown_content,
            extensions=["tables", "fenced_code", "codehilite", "toc", "sane_lists"],
        )

        return f"""
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset='utf-8'>
                <title>Document</title>
            </head>
            <body>
                {html_content}
            </body>
        </html>
        """

    # ----------------- NEW METHODS -----------------

    def read_markdown(self, relative_path: str) -> str | None:
        """Read markdown file by relative path under OUTPUT_DIR/markdown.

        Returns file content as str or None if not found.
        """
        try:
            abs_path = self.OUTPUT_DIR / relative_path
            if not abs_path.exists():
                return None
            with open(abs_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error("Failed to read markdown %s: %s", relative_path, e)
            return None
