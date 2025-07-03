# Features

This repository contains a web-based documentation aggregator with the following major components.

## Backend (`backend/`)

- **FastAPI Service** (`src/main.py`)
  - Endpoints for clipping URLs, uploading files, managing results and organizations.
  - Handles download of generated Markdown or PDF files.
- **Content Processing** (`src/processors`)
  - Extracts main content from HTML using `readability` and cleans it with `bleach`.
  - Deduplicates and formats Markdown output.
- **Utilities** (`src/utils`)
  - Crawling, sitemap parsing and link extraction helpers.
  - Content cleaning and marketing detection using spaCy models.
  - File management for storing Markdown and PDF artifacts.
- **Persistence Layer** (`src/database.py`)
  - SQLite database storing clip metadata, organizations and tags.
- **Configuration** (`config.py`)
  - Defines data paths, models and runtime settings.

## Frontend (`frontend/`)

- **React Application** with TypeScript and Material‑UI.
- Pages for uploading URLs or files, viewing results, managing organizations and settings.
- Interacts with the FastAPI backend via REST calls.

## Deployment

Dockerfiles for both backend and frontend plus `docker-compose.yml` provide a containerised setup.

## Testing

No automated tests are provided yet. A simple validation script is included under [`validate_docs.py`](../validate_docs.py) to check documentation completeness.

Return to the [project README](README.md).
