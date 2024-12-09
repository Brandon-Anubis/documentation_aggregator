# src/web_clipper.py
import logging
from urllib.parse import urlparse
import uuid
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional

from src.web_clipper import WebClipper
from src.utils.file_manager import FileManager
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
    "output_format": "markdown",
    "include_metadata": True,
}
clipper = WebClipper(config)
file_manager = FileManager()


@app.post("/clip")
async def clip_content(request: ClipRequest):
    try:
        result_id = str(uuid.uuid4())

        # Pass tags and other metadata to the clipper for improved formatting
        # The web_clipper internally calls `generate_markdown`.
        result = await clipper.clip(request.input, result_id, tags=request.tags)
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
async def get_results(
    search: str = None,
    organization: str = None,
    sort_by: str = "date",
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
):
    return db.get_results(page, per_page, search, organization)


@app.put("/results/{result_id}")
async def update_result(result_id: str, request: UpdateClipRequest):
    result = db.update_result(result_id, request.dict())
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return {"message": "Result updated successfully"}


@app.delete("/results/{result_id}")
async def delete_result(result_id: str):
    result = db.delete_result(result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return {"message": "Result deleted successfully"}


@app.get("/organizations")
async def get_organizations():
    return db.get_organizations()


@app.post("/organizations")
async def create_organization(org: Organization):
    org_id = str(uuid.uuid4())
    db.add_organization(org_id, org.name, org.description)
    return {"id": org_id, "name": org.name, "description": org.description}


@app.get("/tags")
async def get_tags():
    return db.get_tags()


@app.get("/download/{result_id}/{format}")
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


@app.get("/stats")
async def get_stats():
    return db.get_stats()
