"""
Vercel serverless entrypoint.
Re-exports the FastAPI app from main.py so Vercel can pick it up.
"""
import os
import sys

# Ensure the parent directory (server/) is in the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from main import app
