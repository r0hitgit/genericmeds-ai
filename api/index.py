import sys
import os

# Add parent directory to sys.path so app can be imported cleanly
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from app.main import app

# Expose app for Vercel Python Serverless Runtime
__all__ = ["app"]
