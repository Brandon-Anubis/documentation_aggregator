# Opportunities for Improvement

## Code Quality and Organization
- **Duplicate Main Scripts**: There is a commented-out prototype in `main.py` that can be removed or moved to examples for clarity【F:main.py†L1-L66】.
- **Testing Coverage**: No automated tests are present. Adding unit tests for utilities and API endpoints would greatly improve reliability.
- **Configuration Management**: Sensitive paths and constants are defined directly in `config.py`. Consider using environment variables or a settings library to support multiple environments【F:backend/config.py†L1-L33】.

## Dependency Management
- **Large Model Dependencies**: The backend installs heavy NLP models like `en_core_web_lg` via `requirements.txt`, increasing build times. Evaluate whether smaller models suffice or provide an option to skip installation when not needed【F:backend/requirements.txt†L23-L27】.
- **wkhtmltopdf Runtime**: PDF generation relies on the `wkhtmltopdf` binary installed in the Docker image. Ensure deployments include this dependency and handle errors when unavailable【F:backend/Dockerfile†L1-L19】.

## Backend Design
- **Database Abstraction**: `database.py` directly builds SQL queries with SQLite. Introducing an ORM (e.g., SQLAlchemy) would improve maintainability and make migrations easier【F:backend/src/database.py†L1-L149】.
- **Asynchronous Fetching**: `WebClipper` fetches URLs with a new `aiohttp` session per call. Reusing sessions or implementing connection pooling could improve performance【F:backend/src/web_clipper.py†L25-L37】.

## Frontend Enhancements
- **Form Validation**: Upload and organization forms currently lack validation for required fields. Adding client-side and server-side validation would prevent invalid data.
- **Accessibility**: Ensure components meet accessibility standards (ARIA labels, keyboard navigation) for a wider range of users.

## Documentation
- The project README is minimal. Expanding it with setup instructions and linking to these docs would help newcomers.
