"""
Vercel Serverless Entrypoint for Smart Warehouse Inventory Management Platform.
Exposes the FastAPI ASGI app instance for Vercel's Python runtime.
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import the main FastAPI application instance
from backend.main import app

# Vercel's Python runtime automatically binds to 'app'
