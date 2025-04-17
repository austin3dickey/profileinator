import base64
import logging

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from profileinator.ai_service import generate_profile_images

# Set up logging for the main application
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Profileinator",
    description="Generate profile pictures using AI",
    version="0.1.0",
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="profileinator/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root() -> str:
    """Serve the main page"""
    logger.info("Serving main page")
    with open("profileinator/static/index.html") as file:
        return file.read()


class ImageResponse(BaseModel):
    images: list[str]
    original_filename: str | None


@app.post("/generate/", response_model=ImageResponse)
async def generate_profiles(
    image: UploadFile, num_variants: int
) -> ImageResponse | JSONResponse:
    """Generate profile pictures using AI based on uploaded image"""
    logger.info(f"Received image upload: {image.filename} with {num_variants} variants")

    # Validate file is an image
    if not image.content_type or not image.content_type.startswith("image/"):
        logger.warning(f"Invalid file type: {image.content_type}")
        raise HTTPException(status_code=400, detail="File must be an image")

    # Validate num_variants
    if num_variants < 1 or num_variants > 10:
        logger.warning(f"Invalid number of variants: {num_variants}")
        raise HTTPException(
            status_code=400, detail="Number of variants must be between 1 and 10"
        )

    try:
        # Read the image file
        image_data = await image.read()
        logger.info(f"Read {len(image_data)} bytes from uploaded image")

        # Generate profile images using the AI service
        logger.info(f"Starting profile image generation with {num_variants} variants")
        generated_images = await generate_profile_images(
            image_data, num_variants=num_variants
        )
        logger.info(f"Generated {len(generated_images)} profile images")

        # Convert binary image data to base64 strings for client-side display
        base64_images: list[str] = []
        for i, img in enumerate(generated_images):
            if img:
                encoded_img = base64.b64encode(img).decode("utf-8")
                base64_images.append(encoded_img)
                logger.info(f"Processed variant {i + 1}: {len(img)} bytes")
            else:
                placeholder = base64.b64encode(b"placeholder").decode("utf-8")
                base64_images.append(placeholder)
                logger.warning(f"Variant {i + 1} was empty, using placeholder")

        logger.info("Returning generated images to client")
        return ImageResponse(
            images=base64_images,
            original_filename=image.filename,
        )
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Failed to generate profiles. Please try again."},
        )
