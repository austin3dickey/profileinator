import base64
import logging
import os
import sys
from io import BytesIO
from typing import Any, BinaryIO

from openai import OpenAI

# Set up detailed logging for the AI service
logger = logging.getLogger(__name__)

# Ensure logs go to stderr as well
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Initialize OpenAI client if API key is available
# This allows for easier mocking in tests
if os.getenv("OPENAI_API_KEY"):
    logger.info("Initializing OpenAI client with API key")
    client = OpenAI()
else:
    logger.warning(
        "OPENAI_API_KEY environment variable not set, AI features will be mocked"
    )
    client = None


async def generate_profile_images(
    image_data: BinaryIO | bytes, num_variants: int = 1
) -> list[bytes]:
    """Generate profile image variants using OpenAI's GPT-4o and DALL-E 3 models

    This uses a two-step approach:
    1. GPT-4o analyzes the image and creates detailed prompts
    2. DALL-E 3 generates profile pictures based on those prompts

    Args:
        image_data: Binary image data from user upload, either as bytes or file-like object
        num_variants: Number of variants to generate (default: 1)

    Returns:
        List of generated image data in bytes
    """
    try:
        # If client is None (e.g., no API key), return dummy data for testing
        if client is None:
            logger.warning("OpenAI client not initialized, returning dummy data")
            return [b"" for _ in range(num_variants)]

        # Convert to BytesIO if we got raw bytes
        if isinstance(image_data, bytes):
            image_data = BytesIO(image_data)

        # Create a list to store the generated images
        results: list[bytes] = []

        # Step 1: Analyze the image with GPT-4o to create prompts
        prompts = await analyze_image_with_gpt4o(image_data, num_variants)

        # Step 2: Generate images with DALL-E 3 using the prompts
        for i, prompt in enumerate(prompts):
            try:
                logger.info(f"Generating variant {i + 1} with prompt: {prompt}")
                # Generate an image with DALL-E 3
                image_bytes = await generate_image_with_dalle(prompt)
                results.append(image_bytes)
            except Exception as e:
                logger.warning(f"Error generating variant {i + 1}: {str(e)}")
                # Add empty data for this failed variant
                results.append(b"")

        # If we couldn't generate enough variants, fill with empty data
        while len(results) < num_variants:
            results.append(b"")

        # Return the generated images
        return results

    except Exception as e:
        logger.error(f"Error generating profile images: {str(e)}")
        raise


async def analyze_image_with_gpt4o(
    image_data: BytesIO | BinaryIO, num_variants: int
) -> list[str]:
    """Analyze image with GPT-4o and generate prompts for DALL-E 3

    Args:
        image_data: Image data to analyze
        num_variants: Number of prompt variants to generate

    Returns:
        List of prompts for DALL-E 3
    """
    # Reset file pointer
    image_data.seek(0)

    # Encode image to base64
    base64_image = base64.b64encode(image_data.read()).decode("utf-8")

    # Create system message with instructions
    system_message = """
    You are an expert at analyzing photos and creating detailed prompts for DALL-E 3 to generate professional profile pictures.

    Your task:
    1. Analyze the photo and identify the subject
    2. Create detailed, photorealistic prompts for DALL-E 3 to generate professional profile pictures of the subject
    3. Create a unique prompt style for each variant, covering different professional looks:
       - Corporate/formal
       - Creative professional
       - Friendly but professional
       - Modern minimalist
    4. Do NOT include any names in the prompts
    5. Format your response as a JSON array of prompt strings, with no explanations

    Each prompt should:
    - Be detailed enough for DALL-E 3 to recreate a professional-looking portrait
    - Describe key physical characteristics to maintain likeness
    - Include lighting, composition, and background suggestions
    - Be no more than 150 words
    """

    # Create user message with the image
    user_message = (
        "Create detailed prompts for professional profile pictures based on this photo"
    )

    try:
        # If client is None (e.g., no API key), return dummy data
        if client is None:
            logger.warning("OpenAI client not initialized for analyze_image_with_gpt4o")
            return [
                f"Professional headshot, variant {i + 1}" for i in range(num_variants)
            ]

        # Call the GPT-4o API
        logger.info("Calling GPT-4o for image analysis")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_message},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_message},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                },
            ],
            response_format={"type": "json_object"},
            max_tokens=1500,
        )
        logger.info("Received response from GPT-4o")

        # Parse and extract prompts from the response
        import json

        try:
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from GPT-4o")

            # Parse JSON response
            response_data: Any = json.loads(content)

            # Extract prompts from the response
            raw_prompts: list[Any] = []
            if isinstance(response_data, dict) and "prompts" in response_data:
                raw_prompts = response_data.get("prompts", [])  # type: ignore
            elif isinstance(response_data, list):
                raw_prompts = list(response_data)  # type: ignore
            else:
                raw_prompts = [content]

            # Ensure we have the right number of prompts and they're all strings
            prompts: list[str] = [str(p) for p in raw_prompts[:num_variants]]  # type: ignore
            while len(prompts) < num_variants:
                prompts.append(
                    prompts[0] if prompts else "Professional headshot"
                )  # Duplicate if not enough

            return prompts

        except json.JSONDecodeError:
            # If not valid JSON, just use the raw text as a prompt
            logger.warning("Failed to parse JSON response from GPT-4o")
            return [
                f"Professional headshot, studio lighting, clean background, based on uploaded photo. Variant {i + 1}"
                for i in range(num_variants)
            ]

    except Exception as e:
        logger.error(f"Error analyzing image with GPT-4o: {str(e)}")
        # Fallback to basic prompts
        return [
            f"Professional headshot, studio lighting, clean background. Variant {i + 1}"
            for i in range(num_variants)
        ]


async def generate_image_with_dalle(prompt: str) -> bytes:
    """Generate an image with DALL-E 3 based on the prompt

    Args:
        prompt: The prompt to generate an image from

    Returns:
        The generated image as bytes
    """
    try:
        # If client is None (e.g., no API key), return dummy data
        if client is None:
            logger.warning(
                "OpenAI client not initialized for generate_image_with_dalle"
            )
            return b""

        # Call the DALL-E 3 API
        logger.info("Calling DALL-E 3 for image generation")
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"Create a professional profile picture with the following description: {prompt}",
            n=1,
            size="1024x1024",
            response_format="b64_json",
        )
        logger.info("Received response from DALL-E 3")

        # Extract the image data
        if (
            response.data
            and hasattr(response.data[0], "b64_json")
            and response.data[0].b64_json
        ):
            return base64.b64decode(response.data[0].b64_json)
        else:
            logger.warning("No valid image data in DALL-E response")
            return b""

    except Exception as e:
        logger.error(f"Error generating image with DALL-E: {str(e)}")
        return b""
