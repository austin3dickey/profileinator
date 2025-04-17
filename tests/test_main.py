import pytest
from fastapi.testclient import TestClient

from profileinator.main import app

client = TestClient(app)


def test_read_root():
    """Test that the root endpoint returns the index.html page"""
    response = client.get("/")
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text
    assert "Profileinator" in response.text


def test_generate_profiles_invalid_file():
    """Test that the generate endpoint rejects non-image files"""
    response = client.post(
        "/generate/", files={"image": ("test.txt", b"not an image", "text/plain")}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "File must be an image"


def test_generate_profiles_valid_image(monkeypatch: pytest.MonkeyPatch):
    """Test that the generate endpoint accepts valid image files"""
    # Create a dummy image file for testing
    test_image = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100  # Simple PNG header + content

    response = client.post(
        "/generate/", files={"image": ("test.png", test_image, "image/png")}
    )
    assert response.status_code == 200
    assert "images" in response.json()
    assert isinstance(response.json()["images"], list)
    assert len(response.json()["images"]) > 0
    assert all(isinstance(img, str) for img in response.json()["images"])
    assert "original_filename" in response.json()
    assert response.json()["original_filename"] == "test.png"
