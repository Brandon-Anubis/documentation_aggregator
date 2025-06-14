# Documentation Aggregator

## Overview

The Documentation Aggregator is a Python-based backend service designed to fetch, process, and aggregate documentation from various web sources. It can handle single URLs, lists of URLs, or sitemap.xml files, extracting relevant content and saving it in multiple formats (Markdown, text, PDF).

The system supports fetching content from both static HTML pages and JavaScript-rendered dynamic pages using a combination of `aiohttp` and Playwright.

## Project Structure

- `backend/`: Contains the main application source code.
  - `src/`: Core logic for clipping, processing, and utility functions.
  - `config.py`: Configuration settings for the application.
  - `requirements.txt`: Python dependencies.
- `.local/`: Contains project-specific documentation, diagrams, and progress notes.
- `.gitignore`: Specifies intentionally untracked files that Git should ignore.
- `README.md`: This file.

## Setup

1. **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd documentation_aggregator
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python -m venv .venv
    # On Windows
    .\.venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

3. **Install Python dependencies:**

    ```bash
    pip install -r backend/requirements.txt
    ```

4. **Install Playwright browsers:**
    Playwright requires browser binaries to function. Install them by running:

    ```bash
    playwright install
    ```

    This will download the necessary browser executables (Chromium, Firefox, WebKit).

## Configuration

Key configurations can be found in `backend/config.py`. This includes settings for:

- `USER_AGENT`
- `MAX_CONCURRENT_REQUESTS`
- `OUTPUT_DIR`
- `USE_PLAYWRIGHT_FOR_JS_CONTENT`: A boolean flag to toggle between using Playwright for JavaScript-heavy content or `aiohttp` for all fetching.

## How to Run

(To be defined - e.g., main script execution, API endpoints if applicable)

## Contributing

(To be defined - e.g., coding standards, branch strategy, pull request process)
