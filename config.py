#!/usr/bin/env python3
"""
Configuration Management for AI Screenshot Detector
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
    BASE_DIR = Path(__file__).parent
    
    # ==================================
    # API CONFIGURATION
    # ==================================
    
    # Reality Defender API (Current Provider)
    REALITY_DEFENDER_API_KEY = os.getenv('REALITY_DEFENDER_API_KEY', '')
    
    # ┌─────────────────────────────────────────────────────────────┐
    # │ FUTURE API INTEGRATION PLACEHOLDER                          │
    # ├─────────────────────────────────────────────────────────────┤
    # │ TODO: Implement your custom API integration here            │
    # │                                                              │
    # │ Instructions for implementing custom API:                   │
    # │ 1. Add your API credentials to .env file                    │
    # │ 2. Update these configuration values                        │
    # │ 3. Implement the API client in services/custom_api.py       │
    # │ 4. Update api_server.py to use your custom API              │
    # │                                                              │
    # │ Example environment variables:                              │
    # │   CUSTOM_API_KEY=your_api_key                              │
    # │   CUSTOM_API_URL=https://api.yourservice.com               │
    # │   CUSTOM_API_TIMEOUT=30                                    │
    # └─────────────────────────────────────────────────────────────┘
    
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
    ENABLE_MOCK_MODE = os.getenv('ENABLE_MOCK_MODE', 'false').lower() == 'true'
    
    # ==================================
    # UPLOAD CONFIGURATION
    # ==================================
    
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '16'))
    MAX_CONTENT_LENGTH = MAX_FILE_SIZE_MB * 1024 * 1024
    
    ALLOWED_EXTENSIONS = set(
        os.getenv('ALLOWED_EXTENSIONS', 'png,jpg,jpeg,gif,webp,bmp').split(',')
    )
    
    UPLOAD_FOLDER = Path(os.getenv('UPLOAD_FOLDER', 'uploads'))
    
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
        """
        Validate configuration and return list of warnings/errors
        
        Returns:
            List of validation messages
        """
        messages = []
        
        # Check if API key is configured
        if not cls.REALITY_DEFENDER_API_KEY and not cls.ENABLE_MOCK_MODE:
            messages.append(
                "WARNING: REALITY_DEFENDER_API_KEY not set. "
                "Enable ENABLE_MOCK_MODE=true for demo, or set API key for production."
            )
        
        # Check upload folder
        if not cls.UPLOAD_FOLDER.exists():
            try:
                cls.UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
                messages.append(f"INFO: Created upload folder: {cls.UPLOAD_FOLDER}")
            except Exception as e:
                messages.append(f"ERROR: Cannot create upload folder: {e}")
        
        # Production warnings
        if cls.FLASK_ENV == 'production':
            if cls.FLASK_DEBUG:
                messages.append("WARNING: Debug mode enabled in production environment")
            
            if '*' in cls.CORS_ORIGINS:
                messages.append("WARNING: CORS set to allow all origins. Not recommended for production.")
        
        return messages
    
    @classmethod
    def get_info(cls) -> dict:
        """
        Get configuration information (safe for logging)
        
        Returns:
            Dictionary with configuration info
        """
        return {
            'environment': cls.FLASK_ENV,
            'host': cls.FLASK_HOST,
            'port': cls.FLASK_PORT,
            'debug': cls.FLASK_DEBUG,
            'mock_mode': cls.ENABLE_MOCK_MODE,
            'max_file_size': f"{cls.MAX_FILE_SIZE_MB}MB",
            'allowed_extensions': list(cls.ALLOWED_EXTENSIONS),
            'upload_folder': str(cls.UPLOAD_FOLDER),
            'cors_origins': cls.CORS_ORIGINS,
            'rate_limit': f"{cls.RATE_LIMIT_PER_MINUTE}/min",
            'log_level': cls.LOG_LEVEL,
            'reality_defender_configured': bool(cls.REALITY_DEFENDER_API_KEY),
            'custom_api_configured': bool(cls.CUSTOM_API_KEY),
        }


# Development configuration
class DevelopmentConfig(Config):
    """Development-specific configuration"""
    FLASK_ENV = 'development'
    FLASK_DEBUG = True
    ENABLE_MOCK_MODE = True


# Production configuration
class ProductionConfig(Config):
    """Production-specific configuration"""
    FLASK_ENV = 'production'
    FLASK_DEBUG = False
    ENABLE_MOCK_MODE = False


# Test configuration
class TestConfig(Config):
    """Test-specific configuration"""
    FLASK_ENV = 'testing'
    FLASK_DEBUG = True
    ENABLE_MOCK_MODE = True
    UPLOAD_FOLDER = Path('test_uploads')


# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestConfig,
}


def get_config(env: str | None = None) -> type[Config]:
    """
    Get configuration based on environment
    
    Args:
        env: Environment name (development, production, testing)
        
    Returns:
        Configuration class
    """
    if env is None:
        env = os.getenv('FLASK_ENV', 'production')
    
    return config_map.get(env, Config)
