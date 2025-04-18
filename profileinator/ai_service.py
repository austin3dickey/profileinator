import base64
import logging
import os
from io import BytesIO
from typing import Any, BinaryIO

from fastapi import HTTPException
from openai import OpenAI

# Set up detailed logging for the AI service
logger = logging.getLogger(__name__)

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
    image_data: BinaryIO | bytes, num_variants: int
) -> list[bytes]:
    """Generate profile image variants using OpenAI's GPT-4o and DALL-E 3 models

    This uses a two-step approach:
    1. GPT-4o analyzes the image and creates detailed prompts
    2. DALL-E 3 generates profile pictures based on those prompts

    Args:
        image_data: Binary image data from user upload, either as bytes or file-like object
        num_variants: Number of variants to generate

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

        # If we generated too many variants, truncate the list
        if len(results) > num_variants:
            logger.warning(
                f"Truncating results from {len(results)} to {num_variants} variants"
            )
            results = results[:num_variants]

        # If we couldn't generate enough variants, fill with empty data
        while len(results) < num_variants:
            logger.warning(f"Adding empty placeholder for variant {len(results) + 1}")
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

    # Create system message with instructions, adjusted for the requested number of variants
    professional_styles = [
        "Corporate/formal - Business attire, neutral background, professional lighting",
        "Creative professional - Modern setting, creative lighting, artistic composition",
        "Friendly but professional - Warm colors, approachable pose, soft lighting",
        "Modern minimalist - Clean background, minimalist composition, subtle tones",
        "Executive portrait - Power pose, premium setting, sophisticated lighting",
        "Tech professional - Modern office setting, blue tones, technology-themed",
        "Outdoor professional - Natural light, outdoor business setting, organic feel",
        "Studio portrait - Professional studio lighting, perfect composition, timeless",
    ]

    # Select the appropriate number of style descriptions based on num_variants
    style_descriptions = professional_styles[:num_variants]
    style_bullet_points = "\n".join(
        [f"       - {style}" for style in style_descriptions]
    )

    system_message = f"""
    You are an expert at analyzing photos and creating detailed prompts for DALL-E 3 to generate professional profile pictures.

    Your task:
    1. Analyze the photo. Don't identify anyone in the photo, just describe the physical characteristics.
    2. Create exactly {num_variants} detailed, photorealistic prompts for DALL-E 3
    3. Create a unique prompt style for each variant, covering different professional looks:
{style_bullet_points}
    4. Do NOT include any names in the prompts
    5. Format your response as JSON with the key "prompt", which is an array of prompt strings, with no explanations.

    Example response format:
    ```
    {{
        "prompt": [
            "Professional headshot in corporate style, neutral background, business attire, soft lighting",
            "Creative professional portrait, modern office setting, artistic lighting, friendly expression"
        ]
    }}
    ```

    Each prompt should:
    - Be detailed enough for DALL-E 3 to recreate a professional-looking portrait. There should be at least two paragraphs in each prompt.
    - Describe key physical characteristics to maintain likeness
    - Include specific attire, colors, and styles
    - Include lighting, composition, and background suggestions
    """

    # Create user message with the image
    user_message = (
        "Create detailed prompts for professional profile pictures based on this photo"
    )

    try:
        # If client is None (e.g., no API key), return dummy data
        if client is None:
            logger.warning("OpenAI client not initialized for analyze_image_with_gpt4o")
            # Use our predefined styles for dummy prompts when possible
            return [
                f"Professional headshot in {professional_styles[i % len(professional_styles)]} style"
                for i in range(num_variants)
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
        logger.info("Received response from GPT-4o: %s", response)

        # Parse and extract prompts from the response
        import json

        try:
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from GPT-4o")
            logger.info(f"GPT-4o response content: {content}")

            # Parse JSON response
            response_data: Any = json.loads(content)

            # Extract prompts from the response
            raw_prompts: list[Any] = []
            if isinstance(response_data, dict) and "prompt" in response_data:
                raw_prompts = response_data.get("prompt", [])  # type: ignore
            elif isinstance(response_data, list):
                raw_prompts = list(response_data)  # type: ignore
            else:
                raw_prompts = [content]

            # Ensure we have the right number of prompts and they're all strings
            prompts: list[str] = [str(p) for p in raw_prompts[:num_variants]]  # type: ignore

            # If we don't have enough prompts, generate generic ones to fill in
            if len(prompts) < num_variants:
                logger.warning(
                    f"Only received {len(prompts)} prompts, filling in the rest with generic ones"
                )
                for i in range(len(prompts), num_variants):
                    style = professional_styles[i % len(professional_styles)]
                    prompts.append(f"Professional headshot in {style} style")

            return prompts

        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response from GPT-4o")
            raise

    except Exception as e:
        logger.error(f"Error analyzing image with GPT-4o: {str(e)}")
        raise HTTPException(status_code=400, detail="GPT-4o was uncooperative") from e


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
