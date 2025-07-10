#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the main CAPTCHASolver class.
"""

import os
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path to import captcha_solver
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from captcha_solver import CAPTCHASolver, Config
from captcha_solver.extractor import CAPTCHAExtractor
from captcha_solver.preprocessor import ImagePreprocessor
from captcha_solver.ocr import OCRHandler


class TestCAPTCHASolver(unittest.TestCase):
    """Test cases for the CAPTCHASolver class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.solver = CAPTCHASolver()
        
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
        """Test that the solver initializes correctly."""
        self.assertIsInstance(self.solver.config, Config)
        self.assertIsInstance(self.solver.extractor, CAPTCHAExtractor)
        self.assertIsInstance(self.solver.preprocessor, ImagePreprocessor)
        self.assertIsInstance(self.solver.ocr, OCRHandler)
        
        # Test with custom configuration
        custom_config = {
            "tesseract": {
                "config": "--psm 8"
            },
            "preprocessing": {
                "steps": ["grayscale", "threshold"]
            }
        }
        
        solver = CAPTCHASolver(config=custom_config)
        self.assertEqual(solver.config.get("tesseract.config"), "--psm 8")
        self.assertEqual(solver.config.get("preprocessing.steps"), ["grayscale", "threshold"])
    
    @patch('captcha_solver.solver.Image.open')
    @patch('captcha_solver.ocr.pytesseract.image_to_string')
    def test_solve_from_file(self, mock_image_to_string, mock_open):
        """Test solving CAPTCHA from a file."""
        # Mock the image and OCR result
        mock_image = MagicMock()
        mock_open.return_value = mock_image
        mock_image_to_string.return_value = "ABC123"
        
        # Test solving from file
        result = self.solver.solve_from_file("test.png")
        
        # Verify the result
        self.assertEqual(result, "ABC123")
        mock_open.assert_called_once()
        mock_image_to_string.assert_called_once()
    
    @patch('captcha_solver.extractor.requests.get')
    @patch('captcha_solver.solver.CAPTCHASolver.solve_from_image')
    def test_solve_from_url(self, mock_solve_from_image, mock_get):
        """Test solving CAPTCHA from a URL."""
        # Mock the response and solver result
        mock_response = MagicMock()
        mock_get.return_value = mock_response
        mock_solve_from_image.return_value = "XYZ789"
        
        # Test solving from URL
        result = self.solver.solve_from_url("https://example.com/captcha.png")
        
        # Verify the result
        self.assertEqual(result, "XYZ789")
        mock_get.assert_called_once_with("https://example.com/captcha.png")
        mock_solve_from_image.assert_called_once()
    
    def test_get_statistics(self):
        """Test getting solver statistics."""
        # Add some test data to the history
        self.solver._processing_history = [
            {"result": "ABC123", "confidence": 90.5, "success": True, "time": 0.5},
            {"result": "DEF456", "confidence": 85.2, "success": True, "time": 0.6},
            {"result": "", "confidence": 30.0, "success": False, "time": 0.7}
        ]
        
        # Get statistics
        stats = self.solver.get_statistics()
        
        # Verify statistics
        self.assertEqual(stats["total_processed"], 3)
        self.assertEqual(stats["successful"], 2)
        self.assertEqual(stats["failed"], 1)
        self.assertAlmostEqual(stats["success_rate"], 66.7, places=1)
        self.assertAlmostEqual(stats["average_confidence"], 87.85, places=1)
        self.assertAlmostEqual(stats["average_time"], 0.6, places=1)
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Test with invalid configuration
        invalid_config = {
            "preprocessing": {
                "steps": ["invalid_step"]
            }
        }
        
        # Should not raise an exception, but log a warning
        solver = CAPTCHASolver(config=invalid_config)
        
        # The invalid step should be removed
        self.assertNotIn("invalid_step", solver.config.get("preprocessing.steps"))
    
    @patch('captcha_solver.solver.CAPTCHASolver.solve_from_file')
    def test_solve_batch(self, mock_solve_from_file):
        """Test batch processing of CAPTCHA images."""
        # Create test files
        test_files = []
        for i in range(3):
            file_path = self.test_dir / f"test_{i}.png"
            file_path.touch()
            test_files.append(file_path)
        
        # Mock the solve_from_file method
        mock_solve_from_file.side_effect = [
            "ABC123",  # First result
            "DEF456",  # Second result
            "GHI789"   # Third result
        ]
        
        # Test batch processing
        results = self.solver.solve_batch(test_files)
        
        # Verify results
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]["result"], "ABC123")
        self.assertEqual(results[1]["result"], "DEF456")
        self.assertEqual(results[2]["result"], "GHI789")
        
        # Verify the method was called for each file
        self.assertEqual(mock_solve_from_file.call_count, 3)
    
    def test_system_info(self):
        """Test getting system information."""
        info = self.solver.get_system_info()
        
        # Verify that the info contains expected keys
        self.assertIn("python_version", info)
        self.assertIn("tesseract_version", info)
        self.assertIn("pillow_version", info)
        self.assertIn("opencv_version", info)
        self.assertIn("component_tests", info)


if __name__ == "__main__":
    unittest.main()