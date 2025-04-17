import logging
import os

import uvicorn


def run_server() -> None:
    """Run the Profileinator web server"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler()  # Log to console
        ],
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting Profileinator server")

    # Get port from environment or use default
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"Server will run on port {port}")

    # Start the server
    uvicorn.run(
        "profileinator.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    run_server()
