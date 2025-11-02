#!/usr/bin/env python3
"""
Configuration Management for AI Text Detector
Handles environment variables and application settings
"""

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration"""
    
    # Base directory
    BASE_DIR = Path(__file__).parent.parent
    
    # ==================================
    # API CONFIGURATION
    # ==================================
    
    # Custom API Configuration
    CUSTOM_API_KEY = os.getenv('CUSTOM_API_KEY', '')
    CUSTOM_API_URL = os.getenv('CUSTOM_API_URL', '')
    CUSTOM_API_TIMEOUT = int(os.getenv('CUSTOM_API_TIMEOUT', '30'))
    
    # ==================================
    # SERVER CONFIGURATION
    # ==================================
    
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', '5001'))
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    
    # Enable mock mode for development/demo
    ENABLE_MOCK_MODE = os.getenv('ENABLE_MOCK_MODE', 'true').lower() == 'true'
    
    # ==================================
    # TEXT ANALYSIS CONFIGURATION
    # ==================================
    
    MIN_TEXT_LENGTH = int(os.getenv('MIN_TEXT_LENGTH', '10'))
    MAX_TEXT_LENGTH = int(os.getenv('MAX_TEXT_LENGTH', '50000'))  # 50k characters
    MAX_CONTENT_LENGTH = MAX_TEXT_LENGTH * 4  # Account for encoding overhead
    
    # ==================================
    # SECURITY
    # ==================================
    
    # CORS configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000').split(',')
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    
    # ==================================
    # LOGGING
    # ==================================
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    LOG_FILE = os.getenv('LOG_FILE', '')
    
    # ==================================
    # MONITORING
    # ==================================
    
    ENABLE_MONITORING = os.getenv('ENABLE_MONITORING', 'false').lower() == 'true'
    MONITORING_ENDPOINT = os.getenv('MONITORING_ENDPOINT', '')
    
    @classmethod
    def validate(cls) -> List[str]:
        """Validate configuration and return list of warnings/errors"""
        messages = []
        
        # Check if API is configured
        if not cls.CUSTOM_API_KEY and not cls.ENABLE_MOCK_MODE:
            messages.append(
                "WARNING: CUSTOM_API_KEY not set. "
                "Enable ENABLE_MOCK_MODE=true for demo, or set API key for production."
            )
        
        # Production warnings
        if cls.FLASK_ENV == 'production':
            if cls.FLASK_DEBUG:
                messages.append("WARNING: Debug mode enabled in production environment")
            
            if '*' in cls.CORS_ORIGINS:
                messages.append("WARNING: CORS set to allow all origins. Not recommended for production.")
            
            if cls.ENABLE_MOCK_MODE:
                messages.append("WARNING: Mock mode enabled in production environment")
        
        return messages
    
    @classmethod
    def get_info(cls) -> dict:
        """Get configuration information (safe for logging)"""
        return {
            'environment': cls.FLASK_ENV,
            'host': cls.FLASK_HOST,
            'port': cls.FLASK_PORT,
            'debug': cls.FLASK_DEBUG,
            'mock_mode': cls.ENABLE_MOCK_MODE,
            'min_text_length': f"{cls.MIN_TEXT_LENGTH} chars",
            'max_text_length': f"{cls.MAX_TEXT_LENGTH} chars",
            'cors_origins': cls.CORS_ORIGINS,
            'rate_limit': f"{cls.RATE_LIMIT_PER_MINUTE}/min",
            'log_level': cls.LOG_LEVEL,
            'custom_api_configured': bool(cls.CUSTOM_API_KEY),
        }
