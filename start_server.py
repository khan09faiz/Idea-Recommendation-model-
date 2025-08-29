#!/usr/bin/env python3
"""
Simple launcher script for the FastAPI server.
"""
import sys
import os
from pathlib import Path

# Add the project directory to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import and run the app
from src.app import create_app
import uvicorn

if __name__ == "__main__":
    # Create the FastAPI app
    app = create_app()
    
    print("🚀 Starting Creative Idea Recommendation System...")
    print("📡 Server will be available at: http://127.0.0.1:8001")
    print("📋 API documentation at: http://127.0.0.1:8001/docs")
    print("🛑 Press Ctrl+C to stop the server")
    
    # Run the server
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
        reload=False,  # Disable reload to avoid import issues
        access_log=True
    )
