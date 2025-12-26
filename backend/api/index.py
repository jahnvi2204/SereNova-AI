"""
Vercel serverless function entry point for Flask app.
This wraps the Flask app to work with Vercel's serverless functions.
"""
import sys
import os

# Add parent directory to path to import backend modules
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Change to backend directory for relative imports
os.chdir(backend_dir)

# Import the Flask app
from server import app

# Vercel expects the app to be exported
# The @vercel/python builder will automatically handle Flask apps
__all__ = ['app']

