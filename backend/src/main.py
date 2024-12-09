import logging
import uuid
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from src.web_clipper import WebClipper
from src.utils.file_manager import FileManager
from src.utils.validation import URLValidator
from src.utils.helpers import guess_input_type
from src.utils.input_handler import InputHandler

logger = logging.getLogger(__name__)


class InputRequest(BaseModel):
    input: str


app = FastAPI()

# Allow CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = {
    "output_format": "markdown",  # or 'pdf' if desired by default
    "include_metadata": True,
}
clipper = WebClipper(config)
file_manager = FileManager()

results_storage = {}  # Store result metadata here


@app.post("/clip")
async def clip_endpoint(request: InputRequest):
    input_str = request.input

    # Get the result from the clipper
    result = await clipper.clip(input_str)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to process content")

    # Extract website name from the URL
    from urllib.parse import urlparse

    parsed_url = urlparse(input_str)
    website_name = parsed_url.netloc.replace("www.", "")

    # Generate a unique ID for this result
    result_id = str(uuid.uuid4())

    # Store the result with all necessary information
    result_data = {
        "id": result_id,
        "title": website_name,
        "url": input_str,
        "website_name": website_name,
        "markdown_path": result.get("relative_path"),
        "pdf_path": (
            result.get("relative_path", "")
            .replace("markdown/", "pdf/")
            .replace(".md", ".pdf")
            if result.get("relative_path")
            else None
        ),
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S"),
    }

    results_storage[result_id] = result_data
    return result_data


@app.post("/upload_file")
async def upload_file_endpoint(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    input_path = file_manager.get_input_path(file.filename)
    contents = await file.read()
    with open(input_path, "wb") as f:
        f.write(contents)
    return {"filename": file.filename, "status": "uploaded"}


@app.get("/results")
async def list_results():
    all_results = []
    for r in results_storage.values():
        all_results.append(
            {
                "id": r["id"],
                "title": r["title"],
                "url": r["url"],
                "website_name": r.get("website_name"),
                "markdown_path": r["markdown_path"],
                "pdf_path": r["pdf_path"],
                "timestamp": r["timestamp"],
            }
        )
    return all_results


@app.get("/results/{result_id}")
async def get_result(result_id: str):
    if result_id not in results_storage:
        raise HTTPException(status_code=404, detail="Result not found")
    return results_storage[result_id]


@app.get("/download/{filename:path}")
async def download_file(filename: str):
    # Check for Markdown file
    markdown_path = file_manager.OUTPUT_DIR / filename
    if markdown_path.exists():
        return FileResponse(
            markdown_path, media_type="text/markdown", filename=filename.split("/")[-1]
        )

    # Check for PDF file
    pdf_path = file_manager.OUTPUT_DIR / filename
    if pdf_path.exists():
        return FileResponse(
            pdf_path, media_type="application/pdf", filename=filename.split("/")[-1]
        )

    raise HTTPException(status_code=404, detail="File not found")
