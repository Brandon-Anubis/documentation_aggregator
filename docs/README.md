# Documentation Aggregator

This project provides a full-stack web clipping system. It collects content from websites or sitemaps, cleans it, and stores it as Markdown and PDF. The system also offers a React-based UI for managing clipped results.

## Installation

The recommended setup uses Docker Compose:

```bash
# build and run services
docker-compose up --build
```

Backend will be available on `http://localhost:8000` and the frontend on `http://localhost:3001`.

For manual installation see the [backend](../backend/README.md) and [frontend](../frontend/README.md) docs.

## Usage

- Use the UI to submit URLs or upload files.
- The backend provides REST endpoints documented in the code under `backend/src`.
- Clipped results are stored under `data/` and can be downloaded in Markdown or PDF format.

## Contribution Guidelines

1. Fork the repository and create feature branches.
2. Write tests for new functionality when applicable.
3. Follow the coding style used in the existing codebase.
4. Open a pull request describing your changes.

## Further Reading

- [FEATURES](FEATURES.md) – overview of modules and capabilities.
- [PLAN](PLAN.md) – project roadmap and architecture decisions.
- [TASKS](TASKS.md) – granular task breakdown.
