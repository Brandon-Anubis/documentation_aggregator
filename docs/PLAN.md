# Project Plan: Documentation Aggregator

## Overview
- **Objective**: Provide a service that aggregates web content into clean Markdown and PDF files with metadata.
- **Success Criteria**: Users can clip single URLs or entire sitemaps and view/download results via the UI. Data persists between sessions.
- **Timeline**: Initial prototype delivered; further iterations planned for Q3.
- **Priority**: High

## Technical Analysis
- **Current State**: Working FastAPI backend and React frontend. Core clipping of URLs and sitemaps functions, but several features remain incomplete (see findings below). Tests and CI are missing.
- **Proposed Solution**: Continue containerised deployment using Docker Compose. Finalise PDF generation, integrate content filtering and deduplication, and add robust test coverage.
- **Technology Stack**: Python 3.10, FastAPI, SQLite, React 18, Material‑UI, Docker.
- **Dependencies**: spaCy language model, SentenceTransformer for deduplication, pdfkit for PDF output.

## Implementation Strategy
- **Phase 1**: Stabilise backend API and ensure clipping works for URLs and sitemaps.
- **Phase 2**: Enhance frontend UX and add organization/tag management.
- **Phase 3**: Support JavaScript rendering via a headless browser to capture hidden or dynamically loaded content.
- **Phase 4**: Add automated tests and continuous integration.
- **Phase 5**: Prepare production deployment and monitoring setup.

## Code Review Findings
- **PDF generation** is now integrated using `FileManager.save_pdf`.
- **Marketing detection** (`utils/marketing_detector.py`) is unused; integrate into content processing to filter promotional sections.
- **Semantic deduplication** (`SemanticContentCleaner`) is implemented but never applied when aggregating multiple pages.
- **File uploads** are stored but not processed. Uploaded markdown or sitemap files should trigger clipping logic.
- **Dynamic content** such as JavaScript-driven expansions is ignored because pages are fetched without rendering.  Hidden sections and interactive widgets are therefore lost.
- **Logging and monitoring** are minimal; root `main.py` contains legacy code and should be removed or refactored.

These improvements will enhance output quality, reduce noise in aggregated documentation and simplify maintenance.

## Risk Assessment
- **Technical Risks**: Crawling external sites may fail or be blocked; heavy NLP models and headless browser rendering could impact performance.
- **Business Risks**: Lack of tests may slow future changes; dependency on external websites for data. Legacy code paths could introduce maintenance overhead.
- **Mitigation Strategies**: Implement graceful error handling, integrate monitoring, remove obsolete code, use caching where possible, and incrementally add unit/integration tests.

## Quality Gates
- **Code Review**: Pull requests require at least one approval.
- **Testing**: Aim for 80% coverage of critical modules using pytest and React testing library.
- **Security**: Validate all input URLs and file uploads. Avoid storing secrets in the repo.
- **Performance**: Monitor response times; consider async processing for heavy tasks.

## Status: In Progress
