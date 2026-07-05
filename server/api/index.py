"""
Vercel serverless entrypoint.
Re-exports the FastAPI app from main.py so Vercel can pick it up.
"""
from main import app
