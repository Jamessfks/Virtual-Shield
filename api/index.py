#!/usr/bin/env python3
"""
Vercel Entry Point for Virtual Shield API
This file exports the Flask app for serverless deployment on Vercel
"""

import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app from the main server file
from api_server_v2 import app

# Export the app for Vercel
# Vercel will automatically detect this 'app' variable
# and use it as the entry point for the serverless function
