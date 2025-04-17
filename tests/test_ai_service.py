from io import BytesIO
from typing import Any

import pytest

from profileinator import ai_service
from profileinator.ai_service import generate_profile_images


class MockChatCompletionResponse:
    """Mock ChatCompletion response"""

    class Message:
        def __init__(self, content: str) -> None:
            self.content = content

    class Choice:
        def __init__(self, content: str) -> None:
            self.message = MockChatCompletionResponse.Message(content)

    def __init__(self, content: str) -> None:
        self.choices = [MockChatCompletionResponse.Choice(content)]


class MockImageResponse:
    """Mock image response item"""

    def __init__(self) -> None:
        self.b64_json: str = "test_base64data"


class MockImageData:
    """Mock images API response data"""

    def __init__(self) -> None:
        self.data: list[MockImageResponse] = [MockImageResponse()]


class MockChatCompletions:
    """Mock chat completions API"""

    def create(self, **kwargs: Any) -> MockChatCompletionResponse:
        """Mock create method"""
        return MockChatCompletionResponse(
            '{"prompts": ["Test prompt 1", "Test prompt 2", "Test prompt 3", "Test prompt 4"]}'
        )


class MockImages:
    """Mock OpenAI images API"""

    def generate(self, **kwargs: Any) -> MockImageData:
        """Mock generate method"""
        return MockImageData()


class MockOpenAI:
    """Mock OpenAI client class"""

    def __init__(self) -> None:
        self.images = MockImages()
        self.chat = MockChatCompletions()


@pytest.fixture
def mock_openai_client(monkeypatch: pytest.MonkeyPatch) -> MockOpenAI:
    """Fixture to mock the OpenAI client"""
    # Replace the client with our mock
    monkeypatch.setattr(ai_service, "client", MockOpenAI())
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
    # All should be bytes objects
    assert all(isinstance(img, bytes) for img in result)


@pytest.mark.asyncio
async def test_analyze_image_with_gpt4o(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that the image analysis returns expected prompts"""
    # Set up a mock
    mock_client = MockOpenAI()

    # Create test image data
    image_data = BytesIO(b"test image data")

    # Set the mock client
    monkeypatch.setattr(ai_service, "client", mock_client)

    # Call the function
    prompts = await ai_service.analyze_image_with_gpt4o(image_data, num_variants=4)

    # Verify we get the expected number of prompts
    assert len(prompts) == 4
    assert all(isinstance(prompt, str) for prompt in prompts)


@pytest.mark.asyncio
async def test_generate_image_with_dalle(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that the image generation returns byte data"""
    # Set up a mock
    mock_client = MockOpenAI()

    # Set the mock client
    monkeypatch.setattr(ai_service, "client", mock_client)

    # Call the function
    image_bytes = await ai_service.generate_image_with_dalle("Test prompt")

    # Verify we get bytes back
    assert isinstance(image_bytes, bytes)
