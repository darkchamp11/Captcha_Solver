#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the OCRHandler class.
"""

import os
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image

# Add parent directory to path to import captcha_solver
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from captcha_solver.ocr import OCRHandler
from captcha_solver.config import Config


class TestOCRHandler(unittest.TestCase):
    """Test cases for the OCRHandler class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
        self.ocr_handler = OCRHandler(self.config)
        
        # Create a test image
        self.test_image = Image.new('RGB', (100, 50), color='white')
        
        # Create a test directory for temporary files
        self.test_dir = Path("test_temp")
        self.test_dir.mkdir(exist_ok=True)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up test files
        for file in self.test_dir.glob("*"):
            file.unlink()
        
        if self.test_dir.exists():
            self.test_dir.rmdir()
    
    def test_initialization(self):
        """Test that the OCR handler initializes correctly."""
        self.assertIsInstance(self.ocr_handler.config, Config)
        
        # Test with custom configuration
        custom_config = Config({
            "ocr": {
                "engine": "tesseract",
                "tesseract": {
                    "path": "/usr/bin/tesseract",
                    "config": "--psm 8 --oem 3",
                    "lang": "eng"
                }
            }
        })
        
        ocr_handler = OCRHandler(custom_config)
        self.assertEqual(ocr_handler.config.get("ocr.engine"), "tesseract")
        self.assertEqual(ocr_handler.config.get("ocr.tesseract.path"), "/usr/bin/tesseract")
        self.assertEqual(ocr_handler.config.get("ocr.tesseract.config"), "--psm 8 --oem 3")
        self.assertEqual(ocr_handler.config.get("ocr.tesseract.lang"), "eng")
    
    @patch('captcha_solver.ocr.pytesseract')
    def test_recognize_text_tesseract(self, mock_pytesseract):
        """Test the recognize_text method with Tesseract OCR."""
        # Configure the OCR handler to use Tesseract
        self.ocr_handler.config.set("ocr.engine", "tesseract")
        
        # Set up the mock to return a test result
        mock_pytesseract.image_to_string.return_value = "ABC123"
        
        # Call the recognize_text method
        result = self.ocr_handler.recognize_text(self.test_image)
        
        # Verify that pytesseract.image_to_string was called with the correct arguments
        mock_pytesseract.image_to_string.assert_called_once()
        
        # Verify the result
        self.assertEqual(result, "ABC123")
    
    @patch('captcha_solver.ocr.pytesseract')
    def test_recognize_text_with_custom_config(self, mock_pytesseract):
        """Test the recognize_text method with custom Tesseract configuration."""
        # Configure the OCR handler with custom Tesseract settings
        self.ocr_handler.config.set("ocr.engine", "tesseract")
        self.ocr_handler.config.set("ocr.tesseract.config", "--psm 8 --oem 3")
        self.ocr_handler.config.set("ocr.tesseract.lang", "eng")
        
        # Set up the mock to return a test result
        mock_pytesseract.image_to_string.return_value = "XYZ789"
        
        # Call the recognize_text method
        result = self.ocr_handler.recognize_text(self.test_image)
        
        # Verify that pytesseract.image_to_string was called with the correct arguments
        mock_pytesseract.image_to_string.assert_called_once()
        args, kwargs = mock_pytesseract.image_to_string.call_args
        self.assertEqual(args[0], self.test_image)
        self.assertEqual(kwargs.get('config'), "--psm 8 --oem 3")
        self.assertEqual(kwargs.get('lang'), "eng")
        
        # Verify the result
        self.assertEqual(result, "XYZ789")
    
    @patch('captcha_solver.ocr.pytesseract')
    def test_recognize_text_with_preprocessing(self, mock_pytesseract):
        """Test the recognize_text method with preprocessing."""
        # Configure the OCR handler to use preprocessing
        self.ocr_handler.config.set("ocr.engine", "tesseract")
        self.ocr_handler.config.set("ocr.preprocess", True)
        
        # Set up the mock to return a test result
        mock_pytesseract.image_to_string.return_value = "DEF456"
        
        # Mock the preprocessing method
        with patch.object(self.ocr_handler, '_preprocess_for_ocr') as mock_preprocess:
            # Set up the mock to return a processed image
            processed_image = Image.new('L', (100, 50), color=0)  # Black image
            mock_preprocess.return_value = processed_image
            
            # Call the recognize_text method
            result = self.ocr_handler.recognize_text(self.test_image)
            
            # Verify that _preprocess_for_ocr was called
            mock_preprocess.assert_called_once_with(self.test_image)
            
            # Verify that pytesseract.image_to_string was called with the processed image
            mock_pytesseract.image_to_string.assert_called_once()
            args, kwargs = mock_pytesseract.image_to_string.call_args
            self.assertEqual(args[0], processed_image)
            
            # Verify the result
            self.assertEqual(result, "DEF456")
    
    def test_preprocess_for_ocr(self):
        """Test the _preprocess_for_ocr method."""
        # Call the _preprocess_for_ocr method
        result = self.ocr_handler._preprocess_for_ocr(self.test_image)
        
        # Verify the result is a PIL Image
        self.assertIsInstance(result, Image.Image)
    
    @patch('captcha_solver.ocr.pytesseract')
    def test_recognize_text_with_postprocessing(self, mock_pytesseract):
        """Test the recognize_text method with postprocessing."""
        # Configure the OCR handler to use postprocessing
        self.ocr_handler.config.set("ocr.engine", "tesseract")
        self.ocr_handler.config.set("ocr.postprocess", True)
        
        # Set up the mock to return a test result with noise
        mock_pytesseract.image_to_string.return_value = "G H I 7 8 9"
        
        # Mock the postprocessing method
        with patch.object(self.ocr_handler, '_postprocess_text') as mock_postprocess:
            # Set up the mock to return a cleaned text
            mock_postprocess.return_value = "GHI789"
            
            # Call the recognize_text method
            result = self.ocr_handler.recognize_text(self.test_image)
            
            # Verify that _postprocess_text was called with the raw OCR result
            mock_postprocess.assert_called_once_with("G H I 7 8 9")
            
            # Verify the result
            self.assertEqual(result, "GHI789")
    
    def test_postprocess_text(self):
        """Test the _postprocess_text method."""
        # Test with various input texts
        test_cases = [
            ("A B C 1 2 3", "ABC123"),  # Remove spaces
            ("abc123", "ABC123"),  # Convert to uppercase
            ("ABC!@#123", "ABC123"),  # Remove special characters
            ("ABC\n123", "ABC123"),  # Remove newlines
            ("O0l1I", "OO11I")  # Handle common OCR confusions
        ]
        
        for input_text, expected_output in test_cases:
            # Configure the OCR handler for this test case
            self.ocr_handler.config.set("ocr.postprocess", True)
            self.ocr_handler.config.set("ocr.remove_spaces", True)
            self.ocr_handler.config.set("ocr.uppercase", True)
            self.ocr_handler.config.set("ocr.remove_special_chars", True)
            self.ocr_handler.config.set("ocr.fix_common_errors", True)
            
            # Call the _postprocess_text method
            result = self.ocr_handler._postprocess_text(input_text)
            
            # Verify the result
            self.assertEqual(result, expected_output)
    
    @patch('captcha_solver.ocr.pytesseract')
    def test_recognize_text_with_fallback(self, mock_pytesseract):
        """Test the recognize_text method with fallback to another engine."""
        # Configure the OCR handler to use Tesseract with fallback
        self.ocr_handler.config.set("ocr.engine", "tesseract")
        self.ocr_handler.config.set("ocr.fallback_engine", "custom")
        
        # Set up the mock to return an empty result for the primary engine
        mock_pytesseract.image_to_string.return_value = ""
        
        # Mock the custom OCR method
        with patch.object(self.ocr_handler, '_recognize_with_custom') as mock_custom_ocr:
            # Set up the mock to return a result for the fallback engine
            mock_custom_ocr.return_value = "JKL012"
            
            # Call the recognize_text method
            result = self.ocr_handler.recognize_text(self.test_image)
            
            # Verify that pytesseract.image_to_string was called
            mock_pytesseract.image_to_string.assert_called_once()
            
            # Verify that _recognize_with_custom was called as fallback
            mock_custom_ocr.assert_called_once_with(self.test_image)
            
            # Verify the result
            self.assertEqual(result, "JKL012")
    
    def test_recognize_with_custom(self):
        """Test the _recognize_with_custom method."""
        # Mock a custom OCR implementation
        with patch.object(self.ocr_handler, '_custom_ocr_implementation') as mock_custom_impl:
            # Set up the mock to return a test result
            mock_custom_impl.return_value = "MNO345"
            
            # Set the custom OCR implementation
            self.ocr_handler._custom_ocr_implementation = mock_custom_impl
            
            # Call the _recognize_with_custom method
            result = self.ocr_handler._recognize_with_custom(self.test_image)
            
            # Verify that _custom_ocr_implementation was called
            mock_custom_impl.assert_called_once_with(self.test_image)
            
            # Verify the result
            self.assertEqual(result, "MNO345")


if __name__ == "__main__":
    unittest.main()