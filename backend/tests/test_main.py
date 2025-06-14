# /backend/tests/test_main.py
import os
import pytest
from fastapi.testclient import TestClient
from src.main import app
from config import OUTPUT_DIR

client = TestClient(app)

# A simple, reliable URL for testing
TEST_URL = "http://info.cern.ch/hypertext/WWW/TheProject.html"


def test_clip_endpoint_success():
    """
    Tests the /clip endpoint with a valid URL to ensure it successfully
    creates and saves content, returning a proper response.
    """
    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    response = client.post("/clip", json={"input": TEST_URL, "tags": ["testing", "cern"]})

    # Check for successful response
    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "id" in data
    assert "title" in data
    assert "url" in data
    assert data["url"] == TEST_URL
    assert "markdown_path" in data
    assert "pdf_path" in data
    assert "tags" in data
    assert data["tags"] == ["testing", "cern"]
    assert data["status"] == "success"

    # Verify that files were actually created
    markdown_file_path = os.path.join(OUTPUT_DIR, data["markdown_path"])
    pdf_file_path = os.path.join(OUTPUT_DIR, data["pdf_path"])

    assert os.path.exists(markdown_file_path)
    assert os.path.exists(pdf_file_path)

    # Clean up created files
    os.remove(markdown_file_path)
    os.remove(pdf_file_path)


def test_clip_endpoint_invalid_url():
    """
    Tests the /clip endpoint with an invalid URL to ensure it returns a 500 error.
    """
    response = client.post("/clip", json={"input": "not-a-valid-url"})
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data


def test_get_results_endpoint():
    """
    Tests the /results endpoint to ensure it returns a list of results.
    """
    # First, clip something to ensure there's at least one result
    client.post("/clip", json={"input": TEST_URL})

    response = client.get("/results")
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert len(data["items"]) > 0
