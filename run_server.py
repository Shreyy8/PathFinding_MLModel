#!/usr/bin/env python3
"""
Run script for Interactive Road Mapping Interface Backend API Server.

This script provides a convenient entry point to start the Flask development
server with configurable options.

Usage:
    python run_server.py                    # Start with default settings
    python run_server.py --host 0.0.0.0     # Bind to all interfaces
    python run_server.py --port 8080        # Use custom port
    python run_server.py --debug            # Enable debug mode
    python run_server.py --help             # Show help message

Requirements: 10.1, 10.2, 10.3
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

# Import and run main application
from main import main

if __name__ == '__main__':
    main()
