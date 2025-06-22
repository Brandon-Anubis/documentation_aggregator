# Codebase Overview

## Purpose and Scope
This repository contains a web application that aggregates website content and converts it into downloadable documentation. Users can clip single pages or entire sitemap structures and store the results with metadata. The project includes a FastAPI backend, a React frontend, and a set of utilities for crawling, cleaning, and exporting content.

## Architecture Diagram
```mermaid
flowchart LR
    A[Frontend (React)] -->|REST API| B(Backend FastAPI)
    B --> C[WebClipper]
    C --> D[Content Processor]
    C --> E[File Manager]
    C --> F[Input Handler]
    D --> G[Content Cleaner]
    D --> H[Semantic Deduper]
    B --> I[SQLite DB]
    E --> J[Markdown/PDF files]
```

## Key Modules
- `backend/src/main.py`: FastAPI application with endpoints for clipping content, managing results, and organizations.
- `backend/src/web_clipper.py`: Orchestrates fetching, processing, and saving content.
- `backend/src/processors/content_processor.py`: Extracts readable content from HTML and converts it to Markdown.
- `backend/src/utils`: Helper utilities such as the crawler, sitemap parser, input handler, deduplication, and file manager.
- `frontend/src`: React application providing pages for upload, results, organizations, and settings.
- `backend/src/database.py`: Simple SQLite wrapper for persisting clips and organizations.

## Directory Structure
```
/ (root)
├── backend/        # FastAPI service and utilities
│   ├── src/
│   │   ├── processors/
│   │   ├── utils/
│   │   ├── database.py
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/       # React user interface
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── main.py         # legacy CLI prototype
```

## Dependencies & Prerequisites
- **Backend**: Python 3.10+, FastAPI, Uvicorn, wkhtmltopdf for PDF generation.
- **Frontend**: Node.js 18+, React with Material UI.
- Docker is optional for running services via `docker-compose.yml`.
