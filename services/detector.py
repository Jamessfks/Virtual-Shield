#!/usr/bin/env python3
"""
Detection Service - Unified interface for AI detection
Supports Reality Defender, Custom API, and Mock mode
"""

import logging
import random
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class DetectorService:
    """
    Unified detector service that abstracts different AI detection providers
    
    Supports:
    - Reality Defender API (production)
    - Custom API (your own implementation)
    - Mock mode (development/demo)
    """
    
    def __init__(
        self,
        provider: str = 'reality_defender',
        mock_mode: bool = False,
        **kwargs
    ):
        """
        Initialize detector service
        
        Args:
            provider: Provider name ('reality_defender', 'custom', 'mock')
            mock_mode: Enable mock mode for testing
            **kwargs: Provider-specific configuration
        """
        self.provider = provider
        self.mock_mode = mock_mode
        self.client = None
        
        if mock_mode:
            logger.info("Detector initialized in MOCK mode")
            self.provider = 'mock'
            return
        
        # Initialize provider
        if provider == 'reality_defender':
            self._init_reality_defender(kwargs.get('api_key'))
        elif provider == 'custom':
            self._init_custom_api(kwargs)
        else:
            logger.warning(f"Unknown provider '{provider}', using mock mode")
            self.mock_mode = True
            self.provider = 'mock'
    
    def _init_reality_defender(self, api_key: Optional[str]):
        """Initialize Reality Defender client"""
        if not api_key:
            logger.warning("Reality Defender API key not provided, using mock mode")
            self.mock_mode = True
            self.provider = 'mock'
            return
        
        try:
            from realitydefender import RealityDefender
            self.client = RealityDefender(api_key=api_key)
            logger.info("Reality Defender client initialized successfully")
        except ImportError:
            logger.error("realitydefender package not installed")
            self.mock_mode = True
            self.provider = 'mock'
        except Exception as e:
            logger.error(f"Failed to initialize Reality Defender: {e}")
            self.mock_mode = True
            self.provider = 'mock'
    
    def _init_custom_api(self, config: Dict[str, Any]):
        """Initialize custom API client"""
        try:
            from .custom_api import CustomAPIService
            
            api_key = config.get('api_key')
            api_url = config.get('api_url')
            
            if not api_key or not api_url:
                logger.warning("Custom API not configured, using mock mode")
                self.mock_mode = True
                self.provider = 'mock'
                return
            
            self.client = CustomAPIService(
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
    
    def detect_file(self, file_path: str | Path) -> Dict[str, Any]:
        """
        Detect AI-generated content in image file
        
        Args:
            file_path: Path to image file
            
        Returns:
            Detection result dictionary with:
            {
                'status': 'AUTHENTIC' or 'MANIPULATED',
                'score': float (0.0 to 1.0),
                'confidence': str ('Low', 'Medium', 'High'),
                'provider': str (provider name),
                'metadata': dict (additional data)
            }
        """
        logger.info(f"Analyzing with provider: {self.provider}")
        
        # Mock mode
        if self.mock_mode or self.provider == 'mock':
            return self._generate_mock_result(file_path)
        
        # Reality Defender
        if self.provider == 'reality_defender':
            return self._detect_reality_defender(file_path)
        
        # Custom API
        if self.provider == 'custom':
            return self._detect_custom_api(file_path)
        
        # Fallback to mock
        logger.warning(f"Unknown provider '{self.provider}', using mock")
        return self._generate_mock_result(file_path)
    
    def _detect_reality_defender(self, file_path: str | Path) -> Dict[str, Any]:
        """Detect using Reality Defender API"""
        try:
            result = self.client.detect_file(str(file_path))
            
            status = result.get('status', 'UNKNOWN')
            score = float(result.get('score', 0.0) or 0.0)
            
            return {
                'status': status,
                'score': score,
                'confidence': self._calculate_confidence(score),
                'provider': 'reality_defender',
                'metadata': result
            }
        except Exception as e:
            logger.error(f"Reality Defender detection failed: {e}", exc_info=True)
            # Fallback to mock on error
            logger.warning("Falling back to mock mode")
            return self._generate_mock_result(file_path)
    
    def _detect_custom_api(self, file_path: str | Path) -> Dict[str, Any]:
        """Detect using Custom API"""
        try:
            result = self.client.analyze_image(file_path)
            
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
    
    def _generate_mock_result(self, file_path: str | Path) -> Dict[str, Any]:
        """Generate mock detection result for testing/demo"""
        # Randomize results for demo
        is_ai = random.choice([True, False])
        score = random.uniform(0.6, 0.95) if is_ai else random.uniform(0.0, 0.4)
        
        result = {
            'status': 'MANIPULATED' if is_ai else 'AUTHENTIC',
            'score': score,
            'confidence': self._calculate_confidence(score),
            'provider': 'mock',
            'metadata': {
                'note': 'Mock response for development/demo',
                'mock_mode': True,
                'file_path': str(file_path)
            }
        }
        
        logger.info(f"Mock result: {result['status']} (score: {score:.3f})")
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
        
        if self.provider == 'reality_defender':
            return {
                'healthy': self.client is not None,
                'provider': 'reality_defender',
                'mode': 'production'
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
