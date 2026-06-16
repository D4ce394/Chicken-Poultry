#!/usr/bin/env python3
"""
AI-FRSS Dashboard Backend Server - Mobile Integrated Version
FastAPI backend with WebSocket support, YOLO models, and Mobile APIs
"""

import uvicorn
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    # Get absolute path to app directory
    app_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[app_dir]
    )
