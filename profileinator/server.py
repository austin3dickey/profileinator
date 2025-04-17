import os

import uvicorn


def run_server() -> None:
    """Run the Profileinator web server"""
    # Get port from environment or use default
    port = int(os.getenv("PORT", "8000"))

    # Start the server
    uvicorn.run("profileinator.main:app", host="0.0.0.0", port=port, reload=True)


if __name__ == "__main__":
    run_server()
