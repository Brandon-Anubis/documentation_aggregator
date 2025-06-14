# src/web_clipper.py
import logging
from urllib.parse import urlparse
import uuid
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File, Query, Body
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

from src.web_clipper import WebClipper
from src.utils.file_manager import FileManager
file_manager = FileManager()
from src.utils.validation import URLValidator
from src.utils.helpers import guess_input_type
from src.utils.input_handler import InputHandler
from config import OUTPUT_DIR
from src.database import Database

logger = logging.getLogger(__name__)

# Re-instantiate here because we rely on definitions from current directory
db = Database()


class InputRequest(BaseModel):
    input: str


class Tag(BaseModel):
    name: str


class Organization(BaseModel):
    id: str
    name: str
    description: Optional[str] = None


class ClipRequest(BaseModel):
    input: str
    organization: Optional[str] = None
    tags: Optional[List[str]] = None


class UpdateClipRequest(BaseModel):
    title: Optional[str] = None
    tags: Optional[List[str]] = None
    organization: Optional[str] = None


class MessageResponse(BaseModel):
    message: str


class ClipResponse(BaseModel):
    id: str
    title: str
    url: str
    markdown_path: str
    pdf_path: str
    organization: Optional[str] = None
    tags: List[str]
    timestamp: str
    status: str


class UploadResponse(BaseModel):
    filename: str
    status: str


class ResultItem(BaseModel):
    id: str
    title: str
    url: str
    organization: Optional[str] = None
    tags: List[str]
    timestamp: str


class ResultsResponse(BaseModel):
    total: int
    page: int
    per_page: int
    total_pages: int
    items: List[ResultItem]


class PreviewResponse(BaseModel):
    markdown: str | None = None
    html: str | None = None


app = FastAPI(
    title="Documentation Aggregator API",
    description="""
An API for clipping web content, processing it, and storing it as organized documentation.

You can use this API to:
- **Clip** a URL to save its content.
- **Upload** files for processing.
- **Manage** and search saved results.
- **Organize** content with tags and organizations.
- **Download** content as Markdown or PDF.
    """,
    version="1.1.0",
    contact={
        "name": "Developer Support",
        "url": "https://github.com/Brandon-Anubis/documentation_aggregator",
        "email": "brandon.anubis@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Allow CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

config = {
    "output_format": "markdown",
    "include_metadata": True,
}
clipper = WebClipper(config)


@app.post("/clip", response_model=ClipResponse, summary="Clip and Process a URL", description="Takes a URL, fetches its content, processes it into Markdown and PDF, and saves the result.", tags=["Clipping"])
async def clip_content(request: ClipRequest):
    try:
        result_id = str(uuid.uuid4())

        # Pass tags and other metadata to the clipper for improved formatting
        # The web_clipper internally calls `generate_markdown`.
        result = await clipper.clip(request.input, tags=request.tags)
        if result["status"] == "failed":
            raise HTTPException(status_code=500, detail=result["error"])

        # Store in database
        db_result = {
            "id": result_id,
            "title": result["title"],
            "url": result["url"],
            "markdown_path": result["markdown_path"],
            "pdf_path": result["pdf_path"],
            "organization": request.organization,
            "tags": request.tags or [],
            "timestamp": result["timestamp"],
        }
        db.add_result(result_id, db_result)

        result["id"] = result_id
        return result

    except Exception as e:
        logger.error(f"Error in clip endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload_file", response_model=UploadResponse, summary="Upload a File for Processing", description="Uploads a file (e.g., HTML, text) to the server's input directory for later processing.", tags=["Clipping"])
async def upload_file_endpoint(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    input_path = file_manager.get_input_path(file.filename)
    contents = await file.read()
    with open(input_path, "wb") as f:
        f.write(contents)
    return {"filename": file.filename, "status": "uploaded"}


@app.get("/results", response_model=ResultsResponse, summary="Get a Paginated List of Saved Results", description="Retrieves a list of all saved clipping results, with options for searching, filtering by organization, and sorting.", tags=["Results"])
async def get_results(
    search: str = None,
    organization: str = None,
    sort_by: str = "date",
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
):
    raw = db.get_results(page, per_page, search, organization)
    total = raw.get("total", 0)
    items = raw.get("results", [])

    # Map to ResultItem-compatible dicts (drop markdown_path, pdf_path)
    cleaned_items = [
        {
            "id": r["id"],
            "title": r["title"],
            "url": r["url"],
            "organization": r.get("organization"),
            "tags": r.get("tags", []),
            "timestamp": r.get("timestamp"),
        }
        for r in items
    ]

    # Calculate total pages safely
    total_pages = (total // per_page) + (1 if total % per_page else 0)

    return {
        "items": cleaned_items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages,
    }


@app.put("/results/{result_id}", response_model=MessageResponse, summary="Update a Saved Result", description="Updates the metadata (title, tags, organization) of a specific clipping result.", tags=["Results"])
async def update_result(result_id: str, request: UpdateClipRequest):
    result = db.update_result(result_id, request.dict())
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return {"message": "Result updated successfully"}


@app.delete("/results/{result_id}", response_model=MessageResponse, summary="Delete a Saved Result", description="Deletes a specific clipping result and its associated files from the system.", tags=["Results"])
async def delete_result(result_id: str):
    result = db.delete_result(result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return {"message": "Result deleted successfully"}


@app.get("/organizations", response_model=List[Organization], summary="Get All Organizations", description="Retrieves a list of all created organizations.", tags=["Organizations & Tags"])
async def get_organizations():
    return db.get_organizations()


@app.post("/organizations", response_model=Organization, summary="Create a New Organization", description="Creates a new organization to group clipping results.", tags=["Organizations & Tags"])
async def create_organization(org: Organization):
    org_id = str(uuid.uuid4())
    db.add_organization(org_id, org.name, org.description)
    return {"id": org_id, "name": org.name, "description": org.description}


@app.get("/tags", response_model=List[Tag], summary="Get All Tags", description="Retrieves a list of all unique tags used across all clipping results.", tags=["Organizations & Tags"])
async def get_tags():
    return db.get_tags()


@app.get("/download/{result_id}/{format}", summary="Download a Result File", description="Downloads the generated file (Markdown or PDF) for a specific result.", tags=["Results"])
async def download_file(result_id: str, format: str):
    result = db.get_result(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    file_path = None
    if format == "markdown":
        file_path = os.path.join(OUTPUT_DIR, result["markdown_path"])
    elif format == "pdf":
        file_path = os.path.join(OUTPUT_DIR, result["pdf_path"])
    else:
        raise HTTPException(status_code=400, detail="Invalid format")

    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise HTTPException(
            status_code=404, detail=f"File not found: {os.path.basename(file_path)}"
        )

    return FileResponse(
        file_path,
        filename=os.path.basename(file_path),
        media_type="application/pdf" if format == "pdf" else "text/markdown",
    )


@app.get("/preview/{result_id}", response_model=PreviewResponse, summary="Preview a clipped result", tags=["Results"])
async def preview_result(result_id: str):
    result = db.get_result(result_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")

    md_path = result.get("markdown_path")
    markdown_text = None
    html_text = None
    if md_path:
        markdown_text = file_manager.read_markdown(md_path)
        if markdown_text is not None:
            import markdown as _md

            html_text = _md.markdown(markdown_text, extensions=["tables", "fenced_code", "codehilite"])

    return {"markdown": markdown_text, "html": html_text}


@app.get("/stats", summary="Get System Statistics", description="Retrieves general statistics about the stored data, such as total number of clips, tags, and organizations.", tags=["System"])
async def get_stats():
    return db.get_stats()
