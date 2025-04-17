from io import BytesIO

import pytest

from profileinator.ai_service import generate_profile_images


@pytest.mark.asyncio
async def test_generate_profile_images():
    """Test that the AI service generates the expected number of images"""
    # Create mock image data
    mock_image = BytesIO(b"test image data")

    # Call the function
    result = await generate_profile_images(mock_image, num_variants=4)

    # Check that it returns the expected number of results
    assert len(result) == 4
    # In the initial implementation, these are empty bytes
    assert all(isinstance(img, bytes) for img in result)
