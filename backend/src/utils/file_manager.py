# src/utils/file_manager.py
import os
import markdown
import pdfkit
import logging
from pathlib import Path
from src.utils.helpers import url_to_filename
from config import OUTPUT_DIR, INPUT_DIR, PDFKIT_OPTIONS

logger = logging.getLogger(__name__)


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
            pdfkit.from_string(html_content, str(output_path), options=PDFKIT_OPTIONS)
            return {
                "full_path": str(output_path),
                "relative_path": str(output_path.relative_to(self.OUTPUT_DIR)),
            }
        except Exception as e:
            logger.error(f"Error saving PDF: {e}", exc_info=True)
            return {"full_path": "", "relative_path": ""}

    def _create_styled_html(self, markdown_content: str) -> str:
        html_content = markdown.markdown(
            markdown_content,
            extensions=["tables", "fenced_code", "codehilite", "toc", "sane_lists"],
        )

        return f"""
        <!DOCTYPE html>
        <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 40px;
                        line-height: 1.6;
                        color: #333;
                    }}
                    h1, h2, h3, h4, h5, h6 {{
                        color: #2c3e50;
                        margin-top: 24px;
                        margin-bottom: 16px;
                    }}
                    code {{
                        background-color: #f8f9fa;
                        padding: 2px 4px;
                        border-radius: 4px;
                        font-family: 'Courier New', Courier, monospace;
                    }}
                    pre {{
                        background-color: #f8f9fa;
                        padding: 16px;
                        border-radius: 5px;
                        overflow-x: auto;
                        border: 1px solid #e9ecef;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                        margin: 20px 0;
                    }}
                    th, td {{
                        border: 1px solid #ddd;
                        padding: 8px;
                        text-align: left;
                    }}
                    th {{ background-color: #f8f9fa; }}
                    blockquote {{
                        border-left: 4px solid #eee;
                        padding-left: 15px;
                        margin: 20px 0;
                        color: #666;
                    }}
                    img {{
                        max-width: 100%;
                        height: auto;
                    }}
                    a {{ color: #3498db; text-decoration: none; }}
                    a:hover {{ text-decoration: underline; }}
                    hr {{ border: none; border-top: 1px solid #eee; margin: 30px 0; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
        </html>
        """
