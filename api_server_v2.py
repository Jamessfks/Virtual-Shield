#!/usr/bin/env python3
"""
Flask API Server for AI Screenshot Detection - Production Version
Provides REST API endpoints with improved architecture and security
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import os
import logging
from datetime import datetime
from pathlib import Path
from werkzeug.utils import secure_filename
from functools import wraps
from typing import Tuple, Dict, Any
import time

# Import configuration and services
from config import Config
from services.detector import DetectorService

# ==================================
# LOGGING CONFIGURATION
# ==================================

def setup_logging(config: Config) -> logging.Logger:
    """Configure logging based on config"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    handlers.append(console_handler)
    
    # File handler (if configured)
    if config.LOG_FILE:
        file_handler = logging.FileHandler(config.LOG_FILE)
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=log_format,
        handlers=handlers
    )
    
    return logging.getLogger(__name__)


# ==================================
# FLASK APPLICATION SETUP
# ==================================

def create_app(config_class=Config) -> Tuple[Flask, DetectorService]:
    """
    Application factory pattern
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Tuple of (Flask app, DetectorService)
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_class)
    app.config['MAX_CONTENT_LENGTH'] = config_class.MAX_CONTENT_LENGTH
    app.config['UPLOAD_FOLDER'] = config_class.UPLOAD_FOLDER
    
    # Setup CORS
    CORS(app, origins=config_class.CORS_ORIGINS)
    
    # Setup logging
    logger = setup_logging(config_class)
    
    # Validate configuration
    validation_messages = config_class.validate()
    for msg in validation_messages:
        if msg.startswith('ERROR'):
            logger.error(msg)
        elif msg.startswith('WARNING'):
            logger.warning(msg)
        else:
            logger.info(msg)
    
    # Log configuration
    logger.info("=" * 70)
    logger.info("AI Screenshot Detector API Server - Production Version")
    logger.info("=" * 70)
    for key, value in config_class.get_info().items():
        logger.info(f"  {key:.<30} {value}")
    logger.info("=" * 70)
    
    # Initialize detector service
    logger.info("Initializing detection service...")
    
    # ┌──────────────────────────────────────────────────────────────────┐
    # │ API PROVIDER SELECTION                                           │
    # ├──────────────────────────────────────────────────────────────────┤
    # │ TODO: Change provider when implementing custom API               │
    # │                                                                  │
    # │ Current: 'reality_defender'                                      │
    # │ Custom:  'custom' (when ready)                                   │
    # │ Mock:    Set ENABLE_MOCK_MODE=true in .env                      │
    # └──────────────────────────────────────────────────────────────────┘
    
    if config_class.ENABLE_MOCK_MODE:
        detector = DetectorService(provider='mock', mock_mode=True)
    elif config_class.CUSTOM_API_KEY and config_class.CUSTOM_API_URL:
        # TODO: Uncomment when custom API is implemented
        # detector = DetectorService(
        #     provider='custom',
        #     api_key=config_class.CUSTOM_API_KEY,
        #     api_url=config_class.CUSTOM_API_URL,
        #     timeout=config_class.CUSTOM_API_TIMEOUT
        # )
        logger.warning("Custom API configured but not implemented yet, using Reality Defender")
        detector = DetectorService(
            provider='reality_defender',
            api_key=config_class.REALITY_DEFENDER_API_KEY
        )
    else:
        detector = DetectorService(
            provider='reality_defender',
            api_key=config_class.REALITY_DEFENDER_API_KEY,
            mock_mode=config_class.ENABLE_MOCK_MODE
        )
    
    health_status = detector.health_check()
    logger.info(f"Detector initialized: {health_status}")
    
    return app, detector


# ==================================
# MIDDLEWARE & DECORATORS
# ==================================

# Simple rate limiting (in-memory, for production use Redis/similar)
request_counts: Dict[str, list] = {}

def rate_limit(max_requests: int = 60):
    """
    Rate limiting decorator
    
    Args:
        max_requests: Maximum requests per minute
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Get client IP
            client_ip = request.remote_addr or 'unknown'
            current_time = time.time()
            
            # Initialize or clean old requests
            if client_ip not in request_counts:
                request_counts[client_ip] = []
            
            # Remove requests older than 1 minute
            request_counts[client_ip] = [
                t for t in request_counts[client_ip]
                if current_time - t < 60
            ]
            
            # Check rate limit
            if len(request_counts[client_ip]) >= max_requests:
                logger.warning(f"Rate limit exceeded for {client_ip}")
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Maximum {max_requests} requests per minute'
                }), 429
            
            # Add current request
            request_counts[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        return wrapped
    return decorator


def validate_file(f):
    """Decorator to validate file uploads"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Validate file extension
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Invalid file type',
                'allowed_types': list(Config.ALLOWED_EXTENSIONS)
            }), 400
        
        return f(*args, **kwargs)
    return wrapped


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


# ==================================
# CREATE APPLICATION
# ==================================

app, detector = create_app(Config)
logger = logging.getLogger(__name__)


# ==================================
# API ROUTES
# ==================================

@app.route('/health', methods=['GET'])
def health_check() -> Tuple[Response, int]:
    """
    Health check endpoint
    
    Returns service health status and configuration info
    """
    detector_health = detector.health_check()
    
    return jsonify({
        'status': 'healthy' if detector_health.get('healthy') else 'degraded',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'detector': detector_health,
        'config': {
            'environment': Config.FLASK_ENV,
            'provider': detector.provider,
            'mock_mode': detector.mock_mode
        }
    }), 200


@app.route('/api/analyze', methods=['POST'])
@rate_limit(max_requests=Config.RATE_LIMIT_PER_MINUTE)
@validate_file
def analyze_image() -> Tuple[Response, int]:
    """
    Analyze an image for AI-generated content
    
    Expects:
        - file: Image file in multipart/form-data
    
    Returns:
        JSON with analysis results
    """
    filepath = None
    start_time = time.time()
    
    try:
        logger.info("=" * 70)
        logger.info("New Analysis Request")
        
        file = request.files['file']
        
        # Secure filename
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        logger.info(f"Saving file: {unique_filename}")
        file.save(filepath)
        logger.info(f"File saved: {filepath}")
        
        # Analyze image
        logger.info("Starting analysis...")
        result = detector.detect_file(filepath)
        
        analysis_time = time.time() - start_time
        logger.info(
            f"Analysis complete: {result['status']} "
            f"(score: {result['score']:.3f}, "
            f"confidence: {result['confidence']}, "
            f"time: {analysis_time:.2f}s)"
        )
        
        # Prepare response
        response_data = {
            'success': True,
            'filename': filename,
            'status': result['status'],
            'score': float(result['score']),
            'confidence': result['confidence'],
            'timestamp': datetime.now().isoformat(),
            'size': os.path.getsize(filepath),
            'provider': result.get('provider', 'unknown'),
            'processing_time': analysis_time,
            'fullResult': result.get('metadata', {})
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        
        return jsonify({
            'error': 'Analysis failed',
            'details': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500
        
    finally:
        # Clean up uploaded file
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
                logger.info(f"Cleaned up: {filepath}")
            except Exception as e:
                logger.warning(f"Failed to clean up file: {e}")
        
        logger.info("=" * 70)


@app.route('/api/info', methods=['GET'])
def api_info() -> Tuple[Response, int]:
    """
    Get API information and available endpoints
    """
    return jsonify({
        'name': 'AI Screenshot Detector API',
        'version': '2.0.0',
        'description': 'Production-ready API for detecting AI-generated images',
        'endpoints': {
            '/health': {
                'method': 'GET',
                'description': 'Health check endpoint'
            },
            '/api/analyze': {
                'method': 'POST',
                'description': 'Analyze image for AI content',
                'parameters': {
                    'file': 'Image file (multipart/form-data)'
                },
                'rate_limit': f'{Config.RATE_LIMIT_PER_MINUTE} requests/minute'
            },
            '/api/info': {
                'method': 'GET',
                'description': 'API information (this endpoint)'
            }
        },
        'config': {
            'max_file_size': f'{Config.MAX_FILE_SIZE_MB}MB',
            'allowed_extensions': list(Config.ALLOWED_EXTENSIONS),
            'provider': detector.provider,
            'environment': Config.FLASK_ENV
        }
    }), 200


# ==================================
# ERROR HANDLERS
# ==================================

@app.errorhandler(413)
def request_entity_too_large(error) -> Tuple[Response, int]:
    """Handle file too large error"""
    return jsonify({
        'error': 'File too large',
        'max_size': f'{Config.MAX_FILE_SIZE_MB}MB'
    }), 413


@app.errorhandler(429)
def rate_limit_exceeded(error) -> Tuple[Response, int]:
    """Handle rate limit exceeded"""
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': f'Maximum {Config.RATE_LIMIT_PER_MINUTE} requests per minute'
    }), 429


@app.errorhandler(500)
def internal_server_error(error) -> Tuple[Response, int]:
    """Handle internal server errors"""
    logger.error(f"Internal server error: {error}", exc_info=True)
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


@app.errorhandler(Exception)
def handle_exception(error) -> Tuple[Response, int]:
    """Handle uncaught exceptions"""
    logger.error(f"Uncaught exception: {error}", exc_info=True)
    return jsonify({
        'error': 'Internal server error',
        'message': str(error) if Config.FLASK_DEBUG else 'An unexpected error occurred'
    }), 500


# ==================================
# MAIN ENTRY POINT
# ==================================

if __name__ == '__main__':
    try:
        logger.info("Starting Flask server...")
        logger.info(f"Server URL: http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
        logger.info("Press CTRL+C to stop the server")
        logger.info("=" * 70)
        
        # Run server
        app.run(
            host=Config.FLASK_HOST,
            port=Config.FLASK_PORT,
            debug=Config.FLASK_DEBUG,
            threaded=True,
            use_reloader=False
        )
        
    except KeyboardInterrupt:
        logger.info("\nServer stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise
