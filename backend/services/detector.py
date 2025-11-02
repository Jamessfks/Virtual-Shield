#!/usr/bin/env python3
"""
Text Detection Service - Unified interface for AI text detection
Supports custom API and Mock mode
"""

import logging
import random
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class TextDetectorService:
    """
    Unified text detector service for AI-generated content detection
    
    Supports:
    - Custom API (your own implementation)
    - Mock mode (development/demo)
    """
    
    def __init__(
        self,
        provider: str = 'mock',
        mock_mode: bool = False,
        **kwargs
    ):
        """
        Initialize detector service
        
        Args:
            provider: Provider name ('custom', 'mock')
            mock_mode: Enable mock mode for testing
            **kwargs: Provider-specific configuration
        """
        self.provider = provider
        self.mock_mode = mock_mode
        self.client = None
        
        if mock_mode or provider == 'mock':
            logger.info("Text Detector initialized in MOCK mode")
            self.provider = 'mock'
            return
        
        # Initialize provider
        if provider == 'custom':
            self._init_custom_api(kwargs)
        else:
            logger.warning(f"Unknown provider '{provider}', using mock mode")
            self.mock_mode = True
            self.provider = 'mock'
    
    def _init_custom_api(self, config: Dict[str, Any]):
        """Initialize custom API client"""
        try:
            from .custom_api import CustomTextAPIService
            
            api_key = config.get('api_key')
            api_url = config.get('api_url')
            
            if not api_key or not api_url:
                logger.warning("Custom API not configured, using mock mode")
                self.mock_mode = True
                self.provider = 'mock'
                return
            
            self.client = CustomTextAPIService(
                api_key=api_key,
                api_url=api_url,
                timeout=config.get('timeout', 30)
            )
            logger.info("Custom API client initialized successfully")
        except NotImplementedError:
            logger.warning("Custom API not implemented yet, using mock mode")
            self.mock_mode = True
            self.provider = 'mock'
        except Exception as e:
            logger.error(f"Failed to initialize Custom API: {e}")
            self.mock_mode = True
            self.provider = 'mock'
    
    def detect_text(self, text: str) -> Dict[str, Any]:
        """
        Detect AI-generated content in text
        
        Args:
            text: Text content to analyze
            
        Returns:
            Detection result dictionary with:
            {
                'status': 'AUTHENTIC' or 'AI_GENERATED',
                'score': float (0.0 to 1.0),
                'confidence': str ('Low', 'Medium', 'High'),
                'provider': str (provider name),
                'metadata': dict (additional data)
            }
        """
        logger.info(f"Analyzing text with provider: {self.provider}")
        
        # Mock mode
        if self.mock_mode or self.provider == 'mock':
            return self._generate_mock_result(text)
        
        # Custom API
        if self.provider == 'custom':
            return self._detect_custom_api(text)
        
        # Fallback to mock
        logger.warning(f"Unknown provider '{self.provider}', using mock")
        return self._generate_mock_result(text)
    
    def _detect_custom_api(self, text: str) -> Dict[str, Any]:
        """Detect using Custom API"""
        try:
            result = self.client.analyze_text(text)
            
            return {
                'status': result.get('status', 'UNKNOWN'),
                'score': float(result.get('score', 0.0)),
                'confidence': result.get('confidence', 'Low'),
                'provider': 'custom',
                'metadata': result.get('metadata', {})
            }
        except NotImplementedError:
            logger.error("Custom API not implemented")
            raise
        except Exception as e:
            logger.error(f"Custom API detection failed: {e}", exc_info=True)
            raise
    
    def _generate_mock_result(self, text: str) -> Dict[str, Any]:
        """Generate mock detection result for testing/demo"""
        # Analyze text characteristics for more realistic mock
        word_count = len(text.split())
        
        # More structured text = higher AI probability (mock behavior)
        has_formal_structure = any(phrase in text.lower() for phrase in [
            'furthermore', 'moreover', 'in conclusion', 'therefore', 
            'additionally', 'consequently'
        ])
        
        # Randomize but with some logic
        if has_formal_structure or word_count > 200:
            is_ai = random.choice([True, True, False])  # 66% AI
            score = random.uniform(0.6, 0.95) if is_ai else random.uniform(0.2, 0.5)
        else:
            is_ai = random.choice([True, False, False])  # 33% AI
            score = random.uniform(0.5, 0.85) if is_ai else random.uniform(0.0, 0.4)
        
        result = {
            'status': 'AI_GENERATED' if is_ai else 'AUTHENTIC',
            'score': score,
            'confidence': self._calculate_confidence(score),
            'provider': 'mock',
            'metadata': {
                'note': 'Mock response for development/demo',
                'mock_mode': True,
                'word_count': word_count,
                'text_preview': text[:100] + '...' if len(text) > 100 else text
            }
        }
        
        logger.info(f"Mock result: {result['status']} (score: {score:.3f}, words: {word_count})")
        return result
    
    def _calculate_confidence(self, score: float) -> str:
        """Calculate confidence level from score"""
        if score >= 0.8:
            return "High"
        elif score >= 0.5:
            return "Medium"
        else:
            return "Low"
    
    def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        if self.mock_mode:
            return {
                'healthy': True,
                'provider': 'mock',
                'mode': 'mock'
            }
        
        if self.provider == 'custom' and self.client:
            try:
                return self.client.health_check()
            except:
                return {
                    'healthy': False,
                    'provider': 'custom',
                    'mode': 'production'
                }
        
        return {
            'healthy': False,
            'provider': self.provider,
            'mode': 'unknown'
        }
