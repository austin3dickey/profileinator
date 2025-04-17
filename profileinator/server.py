import uvicorn
import os
from pathlib import Path

def create_static_dir() -> None:
    """Ensure the static directory exists"""
    static_dir = Path("profileinator/static")
    static_dir.mkdir(parents=True, exist_ok=True)

def run_server() -> None:
    """Run the Profileinator web server"""
    # Ensure static directory exists
    create_static_dir()
    
    # Get port from environment or use default
    port = int(os.getenv("PORT", "8000"))
    
    # Start the server
    uvicorn.run(
        "profileinator.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )

if __name__ == "__main__":
    run_server()
