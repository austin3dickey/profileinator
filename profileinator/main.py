import base64

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from profileinator.ai_service import generate_profile_images

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
    with open("profileinator/static/index.html") as file:
        return file.read()


class ImageResponse(BaseModel):
    images: list[str]
    original_filename: str | None


@app.post("/generate/", response_model=ImageResponse)
async def generate_profiles(image: UploadFile) -> ImageResponse | JSONResponse:
    """Generate profile pictures using AI based on uploaded image"""
    # Validate file is an image
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    try:
        # Read the image file
        image_data = await image.read()

        # Generate profile images using the AI service
        generated_images = await generate_profile_images(image_data)

        # Convert binary image data to base64 strings for client-side display
        # In the actual implementation, this will contain real image data
        # For now, these are placeholders
        base64_images = [
            base64.b64encode(img if img else b"placeholder").decode("utf-8")
            for img in generated_images
        ]

        return ImageResponse(
            images=base64_images,
            original_filename=image.filename,
        )
    except Exception as e:
        # Log the error (would implement proper logging)
        print(f"Error processing image: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Failed to generate profiles. Please try again."},
        )
