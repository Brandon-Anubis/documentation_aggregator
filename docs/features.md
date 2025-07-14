# Feature List

## Clipping & Processing
- **URL and Sitemap Clipping**: `/clip` endpoint accepts single URLs or sitemap links and processes them through `WebClipper`【F:backend/src/web_clipper.py†L24-L103】.
- **Content Extraction**: `ContentProcessor` uses `readability` and `html2text` to convert HTML to cleaned Markdown【F:backend/src/processors/content_processor.py†L1-L77】.
- **Marketing & Duplicate Removal**: `ContentCleaner` filters promotional sections and `SemanticContentCleaner` removes near-duplicate sections using embeddings【F:backend/src/utils/content_cleaner.py†L1-L46】【F:backend/src/utils/deduplication.py†L1-L23】.

## File Management
- **Markdown & PDF Output**: Processed content is saved via `FileManager`, generating styled Markdown and optional PDF files【F:backend/src/utils/file_manager.py†L1-L99】.
- **Upload Local Files**: `/upload_file` endpoint stores user-uploaded files for processing later【F:backend/src/main.py†L61-L75】.

## Organization & Metadata
- **Tagging and Organizations**: Results store optional tags and organization IDs, managed through `/organizations` and `/tags` endpoints【F:backend/src/main.py†L79-L115】【F:backend/src/main.py†L134-L151】.
- **Result CRUD**: Endpoints to list, update, delete, and download clipped results【F:backend/src/main.py†L83-L158】.
- **Statistics API**: `/stats` returns totals for clips, organizations, active projects, and storage usage【F:backend/src/main.py†L160-L162】【F:backend/src/database.py†L73-L119】.

## Frontend Features
- **Upload Workflow**: Drag-and-drop or URL input interface for clipping content, with preview dialog on success【F:frontend/src/pages/Upload.tsx†L1-L214】.
- **Results Management**: Search, filter, pagination, edit, and download options for clipped documents【F:frontend/src/pages/Results.tsx†L1-L207】【F:frontend/src/pages/Results.tsx†L200-L292】.
- **Organization Dashboard**: Create, edit, and delete organizations, including basic stats display【F:frontend/src/pages/Organizations.tsx†L1-L199】.
- **User Settings**: Preferences for default formats, storage location, and appearance are editable in the settings page【F:frontend/src/pages/Settings.tsx†L1-L182】.
