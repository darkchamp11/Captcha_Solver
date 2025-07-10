"""OCR (Optical Character Recognition) module for CAPTCHA Solver.

This module handles text extraction from preprocessed CAPTCHA images
using Tesseract OCR with optimized configurations.
"""

import pytesseract
import re
import unicodedata
from PIL import Image
from typing import Optional, Dict, Any, Tuple
import logging
import os
from .utils import Timer, clean_text, normalize_confidence_score


class OCRHandler:
    """OCR handler for extracting text from CAPTCHA images."""
    
    def __init__(self, config: dict):
        """Initialize OCR handler with configuration.
        
        Args:
            config: OCR configuration dictionary.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.last_confidence = 0.0
        self.last_result = ""
        
        # Set Tesseract command path if specified
        tesseract_config = config.get("tesseract", {})
        if "cmd" in tesseract_config and os.path.exists(tesseract_config["cmd"]):
            pytesseract.pytesseract.tesseract_cmd = tesseract_config["cmd"]
        
        # Default Tesseract configuration
        self.default_config = tesseract_config.get(
            "config", 
            "--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        )
    
    def recognize_text(self, image: Image.Image, custom_config: Optional[str] = None) -> str:
        """Extract text from preprocessed image.
        
        Args:
            image: Preprocessed PIL Image.
            custom_config: Custom Tesseract configuration string.
        
        Returns:
            Extracted text string.
        """
        with Timer("OCR text recognition") as timer:
            try:
                # Use custom config or default
                config = custom_config or self.default_config
                
                # Extract text with confidence data
                data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
                
                # Extract text and calculate confidence
                text_parts = []
                confidences = []
                
                for i, word in enumerate(data['text']):
                    if word.strip():  # Skip empty words
                        text_parts.append(word)
                        confidences.append(data['conf'][i])
                
                # Combine text parts
                raw_text = ' '.join(text_parts)
                
                # Calculate average confidence
                if confidences:
                    self.last_confidence = sum(conf for conf in confidences if conf > 0) / len([conf for conf in confidences if conf > 0]) if any(conf > 0 for conf in confidences) else 0
                else:
                    self.last_confidence = 0.0
                
                # Clean and validate text
                cleaned_text = self._clean_ocr_result(raw_text)
                self.last_result = cleaned_text
                
                self.logger.debug(f"OCR completed in {timer.elapsed:.3f}s, confidence: {self.last_confidence:.1f}%")
                self.logger.debug(f"Raw text: '{raw_text}' -> Cleaned: '{cleaned_text}'")
                
                return cleaned_text
                
            except Exception as e:
                self.logger.error(f"OCR recognition failed: {e}")
                self.last_confidence = 0.0
                self.last_result = ""
                return ""
    
    def recognize_with_multiple_configs(self, image: Image.Image) -> Tuple[str, float]:
        """Try multiple OCR configurations and return best result.
        
        Args:
            image: Preprocessed PIL Image.
        
        Returns:
            Tuple of (best_text, best_confidence).
        """
        configs = [
            "--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
            "--psm 7 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
            "--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
            "--psm 8",
            "--psm 7",
            "--psm 13",  # Raw line. Treat the image as a single text line
        ]
        
        best_text = ""
        best_confidence = 0.0
        
        for config in configs:
            try:
                text = self.recognize_text(image, config)
                confidence = self.last_confidence
                
                if confidence > best_confidence and text.strip():
                    best_text = text
                    best_confidence = confidence
                    
            except Exception as e:
                self.logger.debug(f"Config '{config}' failed: {e}")
                continue
        
        self.last_result = best_text
        self.last_confidence = best_confidence
        
        return best_text, best_confidence
    
    def _clean_ocr_result(self, text: str) -> str:
        """Clean and normalize OCR result.
        
        Args:
            text: Raw OCR text.
        
        Returns:
            Cleaned text string.
        """
        if not text:
            return ""
        
        # Normalize unicode characters
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
        
        # Use utility function for basic cleaning
        text = clean_text(text)
        
        # Remove spaces (CAPTCHAs usually don't have spaces)
        text = text.replace(' ', '')
        
        # Remove common OCR misrecognitions
        replacements = {
            '0': 'O',  # Zero to O (context dependent)
            '1': 'I',  # One to I (context dependent)
            '|': 'I',  # Pipe to I
            '!': 'I',  # Exclamation to I
            '@': 'a',  # At symbol to a
            '$': 'S',  # Dollar to S
            '5': 'S',  # Five to S (context dependent)
            '8': 'B',  # Eight to B (context dependent)
        }
        
        # Apply replacements only if they make sense in context
        # This is a simplified approach - more sophisticated logic could be added
        
        return text
    
    def get_confidence(self) -> float:
        """Return OCR confidence score from last recognition.
        
        Returns:
            Confidence score (0-100).
        """
        return self.last_confidence
    
    def get_normalized_confidence(self) -> float:
        """Return normalized confidence score (0-1).
        
        Returns:
            Normalized confidence score.
        """
        return normalize_confidence_score(self.last_confidence, 0, 100)
    
    def configure_tesseract(self, custom_config: str) -> None:
        """Set custom Tesseract parameters.
        
        Args:
            custom_config: Custom Tesseract configuration string.
        """
        self.default_config = custom_config
        self.logger.info(f"Updated Tesseract config: {custom_config}")
    
    def validate_result(self, text: str, expected_length: Optional[int] = None, 
                       pattern: Optional[str] = None) -> bool:
        """Validate OCR result format.
        
        Args:
            text: OCR result text.
            expected_length: Expected text length.
            pattern: Regular expression pattern to match.
        
        Returns:
            True if result is valid, False otherwise.
        """
        if not text or not text.strip():
            return False
        
        # Check length if specified
        if expected_length is not None and len(text) != expected_length:
            return False
        
        # Check pattern if specified
        if pattern is not None:
            if not re.match(pattern, text):
                return False
        
        # Check confidence threshold
        confidence_threshold = self.config.get("ocr", {}).get("confidence_threshold", 60)
        if self.last_confidence < confidence_threshold:
            return False
        
        return True
    
    def extract_numbers_only(self, image: Image.Image) -> str:
        """Extract only numeric characters from image.
        
        Args:
            image: Preprocessed PIL Image.
        
        Returns:
            Numeric text string.
        """
        config = "--psm 8 -c tessedit_char_whitelist=0123456789"
        return self.recognize_text(image, config)
    
    def extract_letters_only(self, image: Image.Image) -> str:
        """Extract only alphabetic characters from image.
        
        Args:
            image: Preprocessed PIL Image.
        
        Returns:
            Alphabetic text string.
        """
        config = "--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        return self.recognize_text(image, config)
    
    def extract_alphanumeric(self, image: Image.Image) -> str:
        """Extract alphanumeric characters from image.
        
        Args:
            image: Preprocessed PIL Image.
        
        Returns:
            Alphanumeric text string.
        """
        config = "--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        return self.recognize_text(image, config)
    
    def get_detailed_results(self, image: Image.Image) -> Dict[str, Any]:
        """Get detailed OCR results including bounding boxes and confidence per character.
        
        Args:
            image: Preprocessed PIL Image.
        
        Returns:
            Dictionary with detailed OCR results.
        """
        try:
            data = pytesseract.image_to_data(image, config=self.default_config, output_type=pytesseract.Output.DICT)
            
            results = {
                "text": "",
                "confidence": 0.0,
                "characters": [],
                "words": [],
                "lines": []
            }
            
            # Process character-level data
            for i in range(len(data['text'])):
                if data['text'][i].strip():
                    char_info = {
                        "text": data['text'][i],
                        "confidence": data['conf'][i],
                        "bbox": {
                            "x": data['left'][i],
                            "y": data['top'][i],
                            "width": data['width'][i],
                            "height": data['height'][i]
                        }
                    }
                    
                    if data['level'][i] == 5:  # Character level
                        results["characters"].append(char_info)
                    elif data['level'][i] == 4:  # Word level
                        results["words"].append(char_info)
                    elif data['level'][i] == 3:  # Line level
                        results["lines"].append(char_info)
            
            # Combine text and calculate average confidence
            all_text = [item["text"] for item in results["characters"]]
            all_conf = [item["confidence"] for item in results["characters"] if item["confidence"] > 0]
            
            results["text"] = "".join(all_text)
            results["confidence"] = sum(all_conf) / len(all_conf) if all_conf else 0.0
            
            return results
            
        except Exception as e:
            self.logger.error(f"Detailed OCR analysis failed: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "characters": [],
                "words": [],
                "lines": []
            }
    
    def is_tesseract_available(self) -> bool:
        """Check if Tesseract is available and working.
        
        Returns:
            True if Tesseract is available, False otherwise.
        """
        try:
            # Try to get Tesseract version
            version = pytesseract.get_tesseract_version()
            self.logger.info(f"Tesseract version: {version}")
            return True
        except Exception as e:
            self.logger.error(f"Tesseract not available: {e}")
            return False
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages.
        
        Returns:
            List of supported language codes.
        """
        try:
            languages = pytesseract.get_languages()
            return languages
        except Exception as e:
            self.logger.error(f"Could not get supported languages: {e}")
            return ["eng"]  # Default to English
    
    def get_ocr_info(self) -> Dict[str, Any]:
        """Get OCR handler information.
        
        Returns:
            Dictionary with OCR information.
        """
        return {
            "tesseract_available": self.is_tesseract_available(),
            "supported_languages": self.get_supported_languages(),
            "default_config": self.default_config,
            "last_confidence": self.last_confidence,
            "last_result": self.last_result,
            "config": self.config
        }