#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the ImagePreprocessor class.
"""

import os
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image, ImageOps
import numpy as np

# Add parent directory to path to import captcha_solver
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from captcha_solver.preprocessor import ImagePreprocessor
from captcha_solver.config import Config


class TestImagePreprocessor(unittest.TestCase):
    """Test cases for the ImagePreprocessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
        self.preprocessor = ImagePreprocessor(self.config)
        
        # Create a test image
        self.test_image = Image.new('RGB', (100, 50), color='white')
        self.test_array = np.array(self.test_image)
        
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
        """Test that the preprocessor initializes correctly."""
        self.assertIsInstance(self.preprocessor.config, Config)
        
        # Test with custom configuration
        custom_config = Config({
            "preprocessing": {
                "steps": ["grayscale", "threshold"],
                "grayscale": {
                    "method": "weighted"
                },
                "threshold": {
                    "method": "binary",
                    "threshold": 150
                }
            }
        })
        
        preprocessor = ImagePreprocessor(custom_config)
        self.assertEqual(preprocessor.config.get("preprocessing.steps"), ["grayscale", "threshold"])
        self.assertEqual(preprocessor.config.get("preprocessing.grayscale.method"), "weighted")
        self.assertEqual(preprocessor.config.get("preprocessing.threshold.method"), "binary")
        self.assertEqual(preprocessor.config.get("preprocessing.threshold.threshold"), 150)
    
    def test_preprocess_image(self):
        """Test the main preprocess_image method."""
        # Mock the individual preprocessing methods
        with patch.object(self.preprocessor, '_apply_grayscale') as mock_grayscale, \
             patch.object(self.preprocessor, '_apply_threshold') as mock_threshold, \
             patch.object(self.preprocessor, '_apply_denoise') as mock_denoise:
            
            # Set up the mocks to return the test image
            mock_grayscale.return_value = self.test_image
            mock_threshold.return_value = self.test_image
            mock_denoise.return_value = self.test_image
            
            # Configure the preprocessor to use these steps
            self.preprocessor.config.set("preprocessing.steps", ["grayscale", "threshold", "denoise"])
            
            # Call the preprocess_image method
            result = self.preprocessor.preprocess_image(self.test_image)
            
            # Verify that each method was called once
            mock_grayscale.assert_called_once_with(self.test_image)
            mock_threshold.assert_called_once_with(self.test_image)
            mock_denoise.assert_called_once_with(self.test_image)
            
            # Verify the result
            self.assertEqual(result, self.test_image)
    
    def test_apply_grayscale(self):
        """Test the grayscale conversion method."""
        # Create a colored test image
        colored_image = Image.new('RGB', (100, 50), color='red')
        
        # Test with default method (weighted)
        result = self.preprocessor._apply_grayscale(colored_image)
        
        # Verify the result is grayscale
        self.assertEqual(result.mode, "L")
        
        # Test with different methods
        for method in ["average", "weighted", "luminosity"]:
            self.preprocessor.config.set("preprocessing.grayscale.method", method)
            result = self.preprocessor._apply_grayscale(colored_image)
            self.assertEqual(result.mode, "L")
    
    def test_apply_threshold(self):
        """Test the thresholding method."""
        # Create a grayscale test image
        grayscale_image = ImageOps.grayscale(self.test_image)
        
        # Test binary thresholding
        self.preprocessor.config.set("preprocessing.threshold.method", "binary")
        self.preprocessor.config.set("preprocessing.threshold.threshold", 128)
        result = self.preprocessor._apply_threshold(grayscale_image)
        
        # Verify the result is still a PIL Image
        self.assertIsInstance(result, Image.Image)
        
        # Test Otsu thresholding
        self.preprocessor.config.set("preprocessing.threshold.method", "otsu")
        result = self.preprocessor._apply_threshold(grayscale_image)
        self.assertIsInstance(result, Image.Image)
        
        # Test adaptive thresholding
        self.preprocessor.config.set("preprocessing.threshold.method", "adaptive")
        self.preprocessor.config.set("preprocessing.threshold.block_size", 11)
        self.preprocessor.config.set("preprocessing.threshold.c_value", 2)
        result = self.preprocessor._apply_threshold(grayscale_image)
        self.assertIsInstance(result, Image.Image)
    
    def test_apply_denoise(self):
        """Test the denoising method."""
        # Create a grayscale test image
        grayscale_image = ImageOps.grayscale(self.test_image)
        
        # Test Gaussian denoising
        self.preprocessor.config.set("preprocessing.denoise.method", "gaussian")
        self.preprocessor.config.set("preprocessing.denoise.kernel_size", 3)
        result = self.preprocessor._apply_denoise(grayscale_image)
        
        # Verify the result is still a PIL Image
        self.assertIsInstance(result, Image.Image)
        
        # Test median denoising
        self.preprocessor.config.set("preprocessing.denoise.method", "median")
        self.preprocessor.config.set("preprocessing.denoise.kernel_size", 3)
        result = self.preprocessor._apply_denoise(grayscale_image)
        self.assertIsInstance(result, Image.Image)
        
        # Test bilateral denoising
        self.preprocessor.config.set("preprocessing.denoise.method", "bilateral")
        result = self.preprocessor._apply_denoise(grayscale_image)
        self.assertIsInstance(result, Image.Image)
    
    def test_apply_morphological_operations(self):
        """Test the morphological operations."""
        # Create a grayscale test image
        grayscale_image = ImageOps.grayscale(self.test_image)
        
        # Test dilation
        self.preprocessor.config.set("preprocessing.morphology.operation", "dilate")
        self.preprocessor.config.set("preprocessing.morphology.kernel_size", 3)
        result = self.preprocessor._apply_morphology(grayscale_image)
        
        # Verify the result is still a PIL Image
        self.assertIsInstance(result, Image.Image)
        
        # Test erosion
        self.preprocessor.config.set("preprocessing.morphology.operation", "erode")
        result = self.preprocessor._apply_morphology(grayscale_image)
        self.assertIsInstance(result, Image.Image)
        
        # Test opening
        self.preprocessor.config.set("preprocessing.morphology.operation", "open")
        result = self.preprocessor._apply_morphology(grayscale_image)
        self.assertIsInstance(result, Image.Image)
        
        # Test closing
        self.preprocessor.config.set("preprocessing.morphology.operation", "close")
        result = self.preprocessor._apply_morphology(grayscale_image)
        self.assertIsInstance(result, Image.Image)
    
    def test_apply_enhance(self):
        """Test the enhancement method."""
        # Create a grayscale test image
        grayscale_image = ImageOps.grayscale(self.test_image)
        
        # Test contrast enhancement
        self.preprocessor.config.set("preprocessing.enhance.method", "contrast")
        self.preprocessor.config.set("preprocessing.enhance.factor", 2.0)
        result = self.preprocessor._apply_enhance(grayscale_image)
        
        # Verify the result is still a PIL Image
        self.assertIsInstance(result, Image.Image)
        
        # Test sharpness enhancement
        self.preprocessor.config.set("preprocessing.enhance.method", "sharpen")
        result = self.preprocessor._apply_enhance(grayscale_image)
        self.assertIsInstance(result, Image.Image)
        
        # Test brightness enhancement
        self.preprocessor.config.set("preprocessing.enhance.method", "brightness")
        result = self.preprocessor._apply_enhance(grayscale_image)
        self.assertIsInstance(result, Image.Image)
    
    def test_clean_noise(self):
        """Test the noise cleaning method."""
        # Create a grayscale test image with some noise
        grayscale_image = ImageOps.grayscale(self.test_image)
        
        # Test noise cleaning
        result = self.preprocessor._clean_noise(grayscale_image)
        
        # Verify the result is still a PIL Image
        self.assertIsInstance(result, Image.Image)
    
    def test_resize_image(self):
        """Test the image resizing method."""
        # Test resizing
        self.preprocessor.config.set("preprocessing.resize.width", 200)
        self.preprocessor.config.set("preprocessing.resize.height", 100)
        result = self.preprocessor._apply_resize(self.test_image)
        
        # Verify the result has the expected dimensions
        self.assertEqual(result.width, 200)
        self.assertEqual(result.height, 100)
        
        # Test resizing with only width specified
        self.preprocessor.config.set("preprocessing.resize.width", 150)
        self.preprocessor.config.set("preprocessing.resize.height", None)
        result = self.preprocessor._apply_resize(self.test_image)
        
        # Verify the result has the expected width and maintains aspect ratio
        self.assertEqual(result.width, 150)
        self.assertEqual(result.height, 75)  # 100 * (150/200) = 75


if __name__ == "__main__":
    unittest.main()