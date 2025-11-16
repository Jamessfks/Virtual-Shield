"""
Text Extraction Service
Extracts text from various file formats (.txt, .pdf, .docx)
"""

import os
import logging
from pathlib import Path
from typing import Optional


logger = logging.getLogger(__name__)


class TextExtractor:
    """Extract text from different file formats"""
    
    @staticmethod
    def extract_from_txt(filepath: str) -> str:
        """Extract text from .txt file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(filepath, 'r', encoding='latin-1') as f:
                return f.read()
    
    @staticmethod
    def extract_from_pdf(filepath: str) -> str:
        """Extract text from .pdf file"""
        try:
            import PyPDF2
            
            text = []
            with open(filepath, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    text.append(page.extract_text())
            
            return '\n'.join(text)
        except ImportError:
            logger.warning("PyPDF2 not installed. PDF extraction unavailable.")
            raise ValueError("PDF extraction not available. Install PyPDF2.")
        except Exception as e:
            logger.error(f"Error extracting PDF: {e}")
            raise
    
    @staticmethod
    def extract_from_docx(filepath: str) -> str:
        """Extract text from .docx file"""
        try:
            from docx import Document
            
            doc = Document(filepath)
            text = []
            for paragraph in doc.paragraphs:
                text.append(paragraph.text)
            
            return '\n'.join(text)
        except ImportError:
            logger.warning("python-docx not installed. DOCX extraction unavailable.")
            raise ValueError("DOCX extraction not available. Install python-docx.")
        except Exception as e:
            logger.error(f"Error extracting DOCX: {e}")
            raise
    
    @classmethod
    def extract_text(cls, filepath: str) -> str:
        """
        Extract text from file based on extension
        
        Args:
            filepath: Path to file
            
        Returns:
            Extracted text content
            
        Raises:
            ValueError: If file format is not supported
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        ext = Path(filepath).suffix.lower()
        
        if ext == '.txt':
            return cls.extract_from_txt(filepath)
        elif ext == '.pdf':
            return cls.extract_from_pdf(filepath)
        elif ext == '.docx':
            return cls.extract_from_docx(filepath)
        else:
            raise ValueError(f"Unsupported file format: {ext}. Supported: .txt, .pdf, .docx")
    
    @staticmethod
    def validate_text(text: str, min_length: int = 10) -> bool:
        """
        Validate extracted text
        
        Args:
            text: Text to validate
            min_length: Minimum text length
            
        Returns:
            True if valid, False otherwise
        """
        if not text or len(text.strip()) < min_length:
            return False
        return True
