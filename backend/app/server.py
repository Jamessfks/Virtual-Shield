#!/usr/bin/env python3
"""
Flask API Server for AI Text Detection
Detects AI-generated text content using various AI detection providers
"""

from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import logging
from datetime import datetime
from functools import wraps
from typing import Tuple, Dict, Any
import time
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Config
from services.detector import TextDetectorService

# ==================================
# LOGGING CONFIGURATION
# ==================================

def setup_logging(config: Config) -> logging.Logger:
    """Configure logging based on config"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    handlers = []
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format))
    handlers.append(console_handler)
    
    if config.LOG_FILE:
        file_handler = logging.FileHandler(config.LOG_FILE)
        file_handler.setFormatter(logging.Formatter(log_format))
        handlers.append(file_handler)
    
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=log_format,
        handlers=handlers
    )
    
    return logging.getLogger(__name__)


# ==================================
# FLASK APPLICATION SETUP
# ==================================

def create_app(config_class=Config) -> Tuple[Flask, TextDetectorService]:
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.config['MAX_CONTENT_LENGTH'] = config_class.MAX_CONTENT_LENGTH
    
    CORS(app, origins=config_class.CORS_ORIGINS)
    logger = setup_logging(config_class)
    
    validation_messages = config_class.validate()
    for msg in validation_messages:
        if msg.startswith('ERROR'):
            logger.error(msg)
        elif msg.startswith('WARNING'):
            logger.warning(msg)
        else:
            logger.info(msg)
    
    logger.info("=" * 70)
    logger.info("AI Text Detector API Server - Production Ready")
    logger.info("=" * 70)
    for key, value in config_class.get_info().items():
        logger.info(f"  {key:.<30} {value}")
    logger.info("=" * 70)
    
    # Initialize detector service
    logger.info("Initializing text detection service...")
    
    if config_class.ENABLE_MOCK_MODE:
        detector = TextDetectorService(provider='mock', mock_mode=True)
    elif config_class.CUSTOM_API_KEY and config_class.CUSTOM_API_URL:
        detector = TextDetectorService(
            provider='custom',
            api_key=config_class.CUSTOM_API_KEY,
            api_url=config_class.CUSTOM_API_URL,
            timeout=config_class.CUSTOM_API_TIMEOUT
        )
    else:
        detector = TextDetectorService(
            provider='mock',  # Default to mock since no specific text detection API configured
            mock_mode=True
        )
    
    health_status = detector.health_check()
    logger.info(f"Detector initialized: {health_status}")
    
    return app, detector


# ==================================
# MIDDLEWARE & DECORATORS
# ==================================

request_counts: Dict[str, list] = {}

def rate_limit(max_requests: int = 60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            client_ip = request.remote_addr or 'unknown'
            current_time = time.time()
            
            if client_ip not in request_counts:
                request_counts[client_ip] = []
            
            request_counts[client_ip] = [
                t for t in request_counts[client_ip]
                if current_time - t < 60
            ]
            
            if len(request_counts[client_ip]) >= max_requests:
                logger.warning(f"Rate limit exceeded for {client_ip}")
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Maximum {max_requests} requests per minute'
                }), 429
            
            request_counts[client_ip].append(current_time)
            return f(*args, **kwargs)
        return wrapped
    return decorator


def validate_text(f):
    """Decorator to validate text input"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({'error': 'Text cannot be empty'}), 400
        
        if len(text) > Config.MAX_TEXT_LENGTH:
            return jsonify({
                'error': 'Text too long',
                'max_length': Config.MAX_TEXT_LENGTH,
                'provided_length': len(text)
            }), 413
        
        if len(text) < Config.MIN_TEXT_LENGTH:
            return jsonify({
                'error': 'Text too short',
                'min_length': Config.MIN_TEXT_LENGTH,
                'provided_length': len(text)
            }), 400
        
        return f(*args, **kwargs)
    return wrapped


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
    """Health check endpoint"""
    detector_health = detector.health_check()
    
    return jsonify({
        'status': 'healthy' if detector_health.get('healthy') else 'degraded',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'service': 'AI Text Detector',
        'detector': detector_health,
        'config': {
            'environment': Config.FLASK_ENV,
            'provider': detector.provider,
            'mock_mode': detector.mock_mode
        }
    }), 200


@app.route('/api/analyze', methods=['POST'])
@rate_limit(max_requests=Config.RATE_LIMIT_PER_MINUTE)
@validate_text
def analyze_text() -> Tuple[Response, int]:
    """
    Analyze text for AI-generated content
    
    Expects:
        JSON: {"text": "text to analyze"}
    
    Returns:
        JSON with analysis results
    """
    start_time = time.time()
    
    try:
        logger.info("=" * 70)
        logger.info("New Text Analysis Request")
        
        data = request.get_json()
        text = data.get('text', '').strip()
        
        logger.info(f"Text length: {len(text)} characters")
        logger.info(f"Text preview: {text[:100]}...")
        
        # Analyze text
        logger.info("Starting analysis...")
        result = detector.detect_text(text)
        
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
            'text_length': len(text),
            'status': result['status'],
            'score': float(result['score']),
            'confidence': result['confidence'],
            'timestamp': datetime.now().isoformat(),
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
        logger.info("=" * 70)


@app.route('/api/info', methods=['GET'])
def api_info() -> Tuple[Response, int]:
    """Get API information and available endpoints"""
    return jsonify({
        'name': 'AI Text Detector API',
        'version': '2.0.0',
        'description': 'Production-ready API for detecting AI-generated text',
        'endpoints': {
            '/health': {
                'method': 'GET',
                'description': 'Health check endpoint'
            },
            '/api/analyze': {
                'method': 'POST',
                'description': 'Analyze text for AI content',
                'parameters': {
                    'text': 'Text content to analyze (JSON body)'
                },
                'rate_limit': f'{Config.RATE_LIMIT_PER_MINUTE} requests/minute',
                'limits': {
                    'min_length': f'{Config.MIN_TEXT_LENGTH} characters',
                    'max_length': f'{Config.MAX_TEXT_LENGTH} characters'
                }
            },
            '/api/info': {
                'method': 'GET',
                'description': 'API information (this endpoint)'
            }
        },
        'config': {
            'max_text_length': f'{Config.MAX_TEXT_LENGTH} chars',
            'min_text_length': f'{Config.MIN_TEXT_LENGTH} chars',
            'provider': detector.provider,
            'environment': Config.FLASK_ENV
        }
    }), 200


# ==================================
# ERROR HANDLERS
# ==================================

@app.errorhandler(413)
def request_entity_too_large(error) -> Tuple[Response, int]:
    """Handle content too large error"""
    return jsonify({
        'error': 'Content too large',
        'max_size': f'{Config.MAX_TEXT_LENGTH} characters'
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
