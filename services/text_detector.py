"""
Text Detection Service
Loads trained AI text detection model and provides inference capabilities
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import numpy as np
import spacy
import textdescriptives as td
import joblib
from tensorflow.keras.models import load_model


logger = logging.getLogger(__name__)


class TextDetectorService:
    """Service for detecting AI-generated text using trained model"""
    
    def __init__(self, model_dir: str = "models"):
        """
        Initialize the text detector service
        
        Args:
            model_dir: Directory containing model artifacts
        """
        self.model_dir = Path(model_dir)
        self.model = None
        self.scaler = None
        self.feature_columns = None
        self.nlp = None
        self.is_ready = False
        
        # Load model and artifacts
        self._load_model()
    
    def _load_model(self):
        """Load model and preprocessing artifacts"""
        try:
            logger.info("Loading text detection model...")
            
            # Check if model files exist
            model_path = self.model_dir / "ai_text_detector.h5"
            scaler_path = self.model_dir / "scaler.pkl"
            columns_path = self.model_dir / "feature_columns.json"
            
            if not all([model_path.exists(), scaler_path.exists(), columns_path.exists()]):
                logger.warning("Model files not found. Please train the model first.")
                return
            
            # Load model
            self.model = load_model(str(model_path))
            logger.info(f"✅ Model loaded from {model_path}")
            
            # Load scaler
            self.scaler = joblib.load(str(scaler_path))
            logger.info(f"✅ Scaler loaded from {scaler_path}")
            
            # Load feature columns
            with open(columns_path, 'r') as f:
                self.feature_columns = json.load(f)
            logger.info(f"✅ Feature columns loaded ({len(self.feature_columns)} features)")
            
            # Load spaCy model with textdescriptives
            logger.info("Loading spaCy model with textdescriptives...")
            self.nlp = spacy.load("en_core_web_sm")
            self.nlp.add_pipe("textdescriptives/all")
            logger.info("✅ spaCy model loaded")
            
            self.is_ready = True
            logger.info("✅ Text detector service ready")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.is_ready = False
            raise
    
    def _extract_features(self, text: str) -> np.ndarray:
        """
        Extract linguistic features from text
        
        Args:
            text: Input text to analyze
            
        Returns:
            Feature array ready for model input
        """
        # Extract features using textdescriptives
        df = td.extract_metrics(text=text, lang="en", metrics=None)
        
        # Drop text column and keep only numeric features
        df_numeric = df.drop(columns=["text"], errors='ignore')
        
        # Align columns with training features and fill missing with 0
        df_aligned = df_numeric.reindex(columns=self.feature_columns).fillna(0)
        
        # Scale features
        scaled = self.scaler.transform(df_aligned)
        
        # Reshape for Conv1D input (1 sample, n_features, 1 channel)
        reshaped = scaled.reshape((1, scaled.shape[1], 1)).astype(np.float32)
        
        return reshaped
    
    def detect_text(self, text: str) -> Dict[str, Any]:
        """
        Detect if text is AI-generated
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with detection results
        """
        if not self.is_ready:
            return {
                'error': 'Model not loaded',
                'message': 'Please train the model first using train_text_detector.py'
            }
        
        try:
            # Validate input
            if not text or len(text.strip()) < 10:
                return {
                    'error': 'Invalid input',
                    'message': 'Text must be at least 10 characters long'
                }
            
            # Extract features
            features = self._extract_features(text)
            
            # Predict
            prediction = self.model.predict(features, verbose=0)[0][0]
            
            # Convert to probability (0 = human, 1 = AI)
            ai_probability = float(prediction)
            human_probability = 1.0 - ai_probability
            
            # Determine classification
            is_ai = ai_probability > 0.5
            
            # Confidence level
            confidence = max(ai_probability, human_probability)
            if confidence >= 0.9:
                confidence_level = "high"
            elif confidence >= 0.7:
                confidence_level = "medium"
            else:
                confidence_level = "low"
            
            return {
                'success': True,
                'classification': 'AI-Generated' if is_ai else 'Human-Written',
                'ai_probability': round(ai_probability, 4),
                'human_probability': round(human_probability, 4),
                'confidence': confidence_level,
                'confidence_score': round(confidence, 4),
                'text_length': len(text),
                'word_count': len(text.split())
            }
            
        except Exception as e:
            logger.error(f"Error during text detection: {e}")
            return {
                'error': 'Detection failed',
                'message': str(e)
            }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check service health status
        
        Returns:
            Health status information
        """
        return {
            'healthy': self.is_ready,
            'model_loaded': self.model is not None,
            'scaler_loaded': self.scaler is not None,
            'nlp_loaded': self.nlp is not None,
            'features_loaded': self.feature_columns is not None,
            'num_features': len(self.feature_columns) if self.feature_columns else 0
        }


# Singleton instance
_text_detector_instance: Optional[TextDetectorService] = None


def get_text_detector() -> TextDetectorService:
    """Get or create text detector singleton instance"""
    global _text_detector_instance
    if _text_detector_instance is None:
        _text_detector_instance = TextDetectorService()
    return _text_detector_instance
