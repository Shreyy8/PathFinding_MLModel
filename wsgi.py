"""
WSGI entry point for production deployment.

This module provides a WSGI-compatible application instance for
production servers like Gunicorn, uWSGI, or mod_wsgi.

Usage with Gunicorn:
    gunicorn --bind 0.0.0.0:5000 --workers 4 wsgi:app

Usage with uWSGI:
    uwsgi --http :5000 --wsgi-file wsgi.py --callable app --processes 4

Requirements: 10.1, 10.2, 10.3
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from src.main import create_app

# Create Flask application
backend_api = create_app()

# Get WSGI application instance
app = backend_api.get_app()

if __name__ == '__main__':
    # For testing WSGI entry point directly
    app.run()
