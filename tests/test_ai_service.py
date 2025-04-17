from io import BytesIO

import pytest

from profileinator import ai_service
from profileinator.ai_service import generate_profile_images


class MockOpenAI:
    """Mock OpenAI client class"""

    def __init__(self):
        pass


@pytest.fixture
def mock_openai_client(monkeypatch: pytest.MonkeyPatch) -> MockOpenAI:
    """Fixture to mock the OpenAI client"""

    # Replace the client with our mock
    monkeypatch.setattr(ai_service, "client", MockOpenAI())

    # Return the mock for further customization if needed
    return MockOpenAI()


@pytest.mark.asyncio
async def test_generate_profile_images(mock_openai_client: MockOpenAI) -> None:
    """Test that the AI service generates the expected number of images"""
    # Create mock image data
    mock_image = BytesIO(b"test image data")

    # Call the function
    result = await generate_profile_images(mock_image, num_variants=4)

    # Check that it returns the expected number of results
    assert len(result) == 4
    # In the initial implementation, these are empty bytes
    assert all(isinstance(img, bytes) for img in result)
