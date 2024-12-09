from pydantic import BaseModel
from typing import List, Optional

class InputRequest(BaseModel):
    input: str  # URL, or possibly a sitemap URL

class ClipResult(BaseModel):
    id: str
    title: str
    url: str
    markdown_path: Optional[str]
    pdf_path: Optional[str]
    timestamp: str

class KBQuery(BaseModel):
    query: str

class KBAddRequest(BaseModel):
    entries: List[ClipResult]

class KBAddResponse(BaseModel):
    status: str

class KBQueryResponse(BaseModel):
    matches: List[dict]

class UploadFileResponse(BaseModel):
    filename: str
    status: str
