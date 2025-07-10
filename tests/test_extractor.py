#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the CAPTCHAExtractor class.
"""

import os
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image
import base64
import io

# Add parent directory to path to import captcha_solver
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from captcha_solver.extractor import CAPTCHAExtractor
from captcha_solver.config import Config


class TestCAPTCHAExtractor(unittest.TestCase):
    """Test cases for the CAPTCHAExtractor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
        self.extractor = CAPTCHAExtractor(self.config)
        
        # Create a test image
        self.test_image = Image.new('RGB', (100, 50), color='white')
        self.test_image_bytes = io.BytesIO()
        self.test_image.save(self.test_image_bytes, format='PNG')
        self.test_image_bytes = self.test_image_bytes.getvalue()
        
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
        """Test that the extractor initializes correctly."""
        self.assertIsInstance(self.extractor.config, Config)
        
        # Test with custom configuration
        custom_config = Config({
            "extraction": {
                "selectors": {
                    "captcha_img": "img.captcha",
                    "captcha_input": "input[name='captcha']"
                },
                "timeout": 10,
                "retries": 3
            }
        })
        
        extractor = CAPTCHAExtractor(custom_config)
        self.assertEqual(extractor.config.get("extraction.selectors.captcha_img"), "img.captcha")
        self.assertEqual(extractor.config.get("extraction.selectors.captcha_input"), "input[name='captcha']")
        self.assertEqual(extractor.config.get("extraction.timeout"), 10)
        self.assertEqual(extractor.config.get("extraction.retries"), 3)
    
    @patch('captcha_solver.extractor.requests.get')
    def test_extract_from_url(self, mock_get):
        """Test the extract_from_url method."""
        # Set up the mock to return a test image
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = self.test_image_bytes
        mock_get.return_value = mock_response
        
        # Call the extract_from_url method
        result = self.extractor.extract_from_url("https://example.com/captcha.png")
        
        # Verify that requests.get was called with the correct URL
        mock_get.assert_called_once_with("https://example.com/captcha.png", timeout=5)
        
        # Verify the result is a PIL Image
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (100, 50))
    
    @patch('captcha_solver.extractor.requests.get')
    def test_extract_from_url_with_error(self, mock_get):
        """Test the extract_from_url method with an error response."""
        # Set up the mock to return an error response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Call the extract_from_url method and expect an exception
        with self.assertRaises(Exception):
            self.extractor.extract_from_url("https://example.com/captcha.png")
    
    @patch('captcha_solver.extractor.requests.get')
    @patch('captcha_solver.extractor.BeautifulSoup')
    def test_extract_from_webpage(self, mock_bs, mock_get):
        """Test the extract_from_webpage method."""
        # Set up the mock for the webpage response
        mock_webpage_response = MagicMock()
        mock_webpage_response.status_code = 200
        mock_webpage_response.content = b"<html><body><img class='captcha' src='captcha.png'></body></html>"
        mock_get.side_effect = [mock_webpage_response, MagicMock(status_code=200, content=self.test_image_bytes)]
        
        # Set up the mock for BeautifulSoup
        mock_soup = MagicMock()
        mock_img = MagicMock()
        mock_img.get.return_value = "captcha.png"
        mock_soup.select_one.return_value = mock_img
        mock_bs.return_value = mock_soup
        
        # Call the extract_from_webpage method
        result = self.extractor.extract_from_webpage("https://example.com/form")
        
        # Verify that requests.get was called for the webpage and the image
        self.assertEqual(mock_get.call_count, 2)
        
        # Verify that BeautifulSoup was called to parse the HTML
        mock_bs.assert_called_once()
        
        # Verify that the selector was used to find the CAPTCHA image
        mock_soup.select_one.assert_called_once_with("img.captcha")
        
        # Verify the result is a PIL Image
        self.assertIsInstance(result, Image.Image)
    
    def test_extract_from_element_screenshot(self):
        """Test the extract_from_element method with screenshot."""
        # Create a mock Selenium WebElement
        mock_element = MagicMock()
        mock_element.screenshot_as_png = self.test_image_bytes
        
        # Call the extract_from_element method with screenshot method
        result = self.extractor.extract_from_element(mock_element, method="screenshot")
        
        # Verify that screenshot_as_png was accessed
        mock_element.screenshot_as_png  # Access the property
        
        # Verify the result is a PIL Image
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (100, 50))
    
    def test_extract_from_element_src(self):
        """Test the extract_from_element method with src attribute."""
        # Create a mock Selenium WebElement
        mock_element = MagicMock()
        mock_element.get_attribute.return_value = "data:image/png;base64," + base64.b64encode(self.test_image_bytes).decode()
        
        # Call the extract_from_element method with src method
        result = self.extractor.extract_from_element(mock_element, method="src")
        
        # Verify that get_attribute was called with "src"
        mock_element.get_attribute.assert_called_once_with("src")
        
        # Verify the result is a PIL Image
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (100, 50))
    
    def test_extract_from_element_background(self):
        """Test the extract_from_element method with background image."""
        # Create a mock Selenium WebElement
        mock_element = MagicMock()
        mock_element.value_of_css_property.return_value = "url(data:image/png;base64," + base64.b64encode(self.test_image_bytes).decode() + ")"
        
        # Call the extract_from_element method with background method
        result = self.extractor.extract_from_element(mock_element, method="background")
        
        # Verify that value_of_css_property was called with "background-image"
        mock_element.value_of_css_property.assert_called_once_with("background-image")
        
        # Verify the result is a PIL Image
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (100, 50))
    
    def test_decode_data_uri(self):
        """Test the _decode_data_uri method."""
        # Create a data URI
        data_uri = "data:image/png;base64," + base64.b64encode(self.test_image_bytes).decode()
        
        # Call the _decode_data_uri method
        result = self.extractor._decode_data_uri(data_uri)
        
        # Verify the result is a PIL Image
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (100, 50))
    
    def test_decode_data_uri_invalid(self):
        """Test the _decode_data_uri method with an invalid data URI."""
        # Call the _decode_data_uri method with an invalid data URI
        with self.assertRaises(ValueError):
            self.extractor._decode_data_uri("not-a-data-uri")
    
    @patch('captcha_solver.extractor.requests.get')
    def test_download_image(self, mock_get):
        """Test the _download_image method."""
        # Set up the mock to return a test image
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = self.test_image_bytes
        mock_get.return_value = mock_response
        
        # Call the _download_image method
        result = self.extractor._download_image("https://example.com/captcha.png")
        
        # Verify that requests.get was called with the correct URL
        mock_get.assert_called_once_with("https://example.com/captcha.png", timeout=5)
        
        # Verify the result is image bytes
        self.assertEqual(result, self.test_image_bytes)
    
    @patch('captcha_solver.extractor.requests.get')
    def test_download_image_with_error(self, mock_get):
        """Test the _download_image method with an error response."""
        # Set up the mock to return an error response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Call the _download_image method and expect an exception
        with self.assertRaises(Exception):
            self.extractor._download_image("https://example.com/captcha.png")
    
    def test_bytes_to_image(self):
        """Test the _bytes_to_image method."""
        # Call the _bytes_to_image method
        result = self.extractor._bytes_to_image(self.test_image_bytes)
        
        # Verify the result is a PIL Image
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (100, 50))
    
    def test_bytes_to_image_invalid(self):
        """Test the _bytes_to_image method with invalid image data."""
        # Call the _bytes_to_image method with invalid image data
        with self.assertRaises(Exception):
            self.extractor._bytes_to_image(b"not-an-image")
    
    def test_find_captcha_element(self):
        """Test the find_captcha_element method."""
        # Create a mock Selenium WebDriver
        mock_driver = MagicMock()
        mock_element = MagicMock()
        mock_driver.find_element.return_value = mock_element
        
        # Call the find_captcha_element method
        result = self.extractor.find_captcha_element(mock_driver)
        
        # Verify that find_element was called with the correct selector
        mock_driver.find_element.assert_called_once()
        
        # Verify the result is the mock element
        self.assertEqual(result, mock_element)
    
    def test_find_captcha_element_with_custom_selector(self):
        """Test the find_captcha_element method with a custom selector."""
        # Create a mock Selenium WebDriver
        mock_driver = MagicMock()
        mock_element = MagicMock()
        mock_driver.find_element.return_value = mock_element
        
        # Call the find_captcha_element method with a custom selector
        result = self.extractor.find_captcha_element(mock_driver, selector="#custom-captcha")
        
        # Verify that find_element was called with the custom selector
        mock_driver.find_element.assert_called_once()
        
        # Verify the result is the mock element
        self.assertEqual(result, mock_element)
    
    def test_find_captcha_element_not_found(self):
        """Test the find_captcha_element method when the element is not found."""
        # Create a mock Selenium WebDriver
        mock_driver = MagicMock()
        mock_driver.find_element.side_effect = Exception("Element not found")
        
        # Call the find_captcha_element method and expect an exception
        with self.assertRaises(Exception):
            self.extractor.find_captcha_element(mock_driver)
    
    @patch('captcha_solver.extractor.webdriver.Chrome')
    def test_extract_with_selenium(self, mock_chrome):
        """Test the extract_with_selenium method."""
        # Set up the mock for Chrome WebDriver
        mock_driver = MagicMock()
        mock_element = MagicMock()
        mock_element.screenshot_as_png = self.test_image_bytes
        mock_driver.find_element.return_value = mock_element
        mock_chrome.return_value = mock_driver
        
        # Call the extract_with_selenium method
        result = self.extractor.extract_with_selenium("https://example.com/form")
        
        # Verify that Chrome was instantiated
        mock_chrome.assert_called_once()
        
        # Verify that the driver navigated to the URL
        mock_driver.get.assert_called_once_with("https://example.com/form")
        
        # Verify that find_element was called
        mock_driver.find_element.assert_called_once()
        
        # Verify that the driver was quit
        mock_driver.quit.assert_called_once()
        
        # Verify the result is a PIL Image
        self.assertIsInstance(result, Image.Image)
        self.assertEqual(result.size, (100, 50))


if __name__ == "__main__":
    unittest.main()