#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the FormSubmitter class.
"""

import os
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from PIL import Image

# Add parent directory to path to import captcha_solver
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from captcha_solver.submitter import FormSubmitter
from captcha_solver.config import Config


class TestFormSubmitter(unittest.TestCase):
    """Test cases for the FormSubmitter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = Config()
        self.submitter = FormSubmitter(self.config)
        
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
        """Test that the submitter initializes correctly."""
        self.assertIsInstance(self.submitter.config, Config)
        
        # Test with custom configuration
        custom_config = Config({
            "submission": {
                "selectors": {
                    "captcha_input": "input[name='captcha']",
                    "submit_button": "button[type='submit']"
                },
                "timeout": 10,
                "wait_after_submit": 5
            }
        })
        
        submitter = FormSubmitter(custom_config)
        self.assertEqual(submitter.config.get("submission.selectors.captcha_input"), "input[name='captcha']")
        self.assertEqual(submitter.config.get("submission.selectors.submit_button"), "button[type='submit']")
        self.assertEqual(submitter.config.get("submission.timeout"), 10)
        self.assertEqual(submitter.config.get("submission.wait_after_submit"), 5)
    
    def test_submit_captcha_solution(self):
        """Test the submit_captcha_solution method."""
        # Create a mock Selenium WebDriver
        mock_driver = MagicMock()
        mock_input = MagicMock()
        mock_button = MagicMock()
        mock_driver.find_element.side_effect = [mock_input, mock_button]
        
        # Call the submit_captcha_solution method
        self.submitter.submit_captcha_solution(mock_driver, "ABC123")
        
        # Verify that find_element was called twice (for input and button)
        self.assertEqual(mock_driver.find_element.call_count, 2)
        
        # Verify that the input was cleared and the solution was sent
        mock_input.clear.assert_called_once()
        mock_input.send_keys.assert_called_once_with("ABC123")
        
        # Verify that the submit button was clicked
        mock_button.click.assert_called_once()
    
    def test_submit_captcha_solution_with_custom_selectors(self):
        """Test the submit_captcha_solution method with custom selectors."""
        # Create a mock Selenium WebDriver
        mock_driver = MagicMock()
        mock_input = MagicMock()
        mock_button = MagicMock()
        mock_driver.find_element.side_effect = [mock_input, mock_button]
        
        # Call the submit_captcha_solution method with custom selectors
        self.submitter.submit_captcha_solution(
            mock_driver, 
            "XYZ789", 
            input_selector="#custom-captcha", 
            submit_selector="#custom-submit"
        )
        
        # Verify that find_element was called with the custom selectors
        mock_driver.find_element.assert_any_call("css selector", "#custom-captcha")
        mock_driver.find_element.assert_any_call("css selector", "#custom-submit")
        
        # Verify that the input was cleared and the solution was sent
        mock_input.clear.assert_called_once()
        mock_input.send_keys.assert_called_once_with("XYZ789")
        
        # Verify that the submit button was clicked
        mock_button.click.assert_called_once()
    
    def test_submit_captcha_solution_input_not_found(self):
        """Test the submit_captcha_solution method when the input is not found."""
        # Create a mock Selenium WebDriver
        mock_driver = MagicMock()
        mock_driver.find_element.side_effect = Exception("Element not found")
        
        # Call the submit_captcha_solution method and expect an exception
        with self.assertRaises(Exception):
            self.submitter.submit_captcha_solution(mock_driver, "ABC123")
    
    def test_fill_form_fields(self):
        """Test the fill_form_fields method."""
        # Create a mock Selenium WebDriver
        mock_driver = MagicMock()
        mock_input1 = MagicMock()
        mock_input2 = MagicMock()
        mock_driver.find_element.side_effect = [mock_input1, mock_input2]
        
        # Call the fill_form_fields method
        self.submitter.fill_form_fields(mock_driver, {
            "username": "testuser",
            "password": "testpass"
        })
        
        # Verify that find_element was called for each field
        self.assertEqual(mock_driver.find_element.call_count, 2)
        
        # Verify that the inputs were cleared and the values were sent
        mock_input1.clear.assert_called_once()
        mock_input1.send_keys.assert_called_once()
        mock_input2.clear.assert_called_once()
        mock_input2.send_keys.assert_called_once()
    
    def test_fill_form_fields_with_custom_selectors(self):
        """Test the fill_form_fields method with custom selectors."""
        # Create a mock Selenium WebDriver
        mock_driver = MagicMock()
        mock_input1 = MagicMock()
        mock_input2 = MagicMock()
        mock_driver.find_element.side_effect = [mock_input1, mock_input2]
        
        # Call the fill_form_fields method with custom selectors
        self.submitter.fill_form_fields(mock_driver, {
            "username": {"value": "testuser", "selector": "#custom-username"},
            "password": {"value": "testpass", "selector": "#custom-password"}
        })
        
        # Verify that find_element was called with the custom selectors
        mock_driver.find_element.assert_any_call("css selector", "#custom-username")
        mock_driver.find_element.assert_any_call("css selector", "#custom-password")
        
        # Verify that the inputs were cleared and the values were sent
        mock_input1.clear.assert_called_once()
        mock_input1.send_keys.assert_called_once_with("testuser")
        mock_input2.clear.assert_called_once()
        mock_input2.send_keys.assert_called_once_with("testpass")
    
    def test_fill_form_fields_field_not_found(self):
        """Test the fill_form_fields method when a field is not found."""
        # Create a mock Selenium WebDriver
        mock_driver = MagicMock()
        mock_driver.find_element.side_effect = Exception("Element not found")
        
        # Call the fill_form_fields method and expect an exception
        with self.assertRaises(Exception):
            self.submitter.fill_form_fields(mock_driver, {"username": "testuser"})
    
    @patch('captcha_solver.submitter.WebDriverWait')
    def test_wait_for_result(self, mock_wait):
        """Test the wait_for_result method."""
        # Create a mock Selenium WebDriver and WebDriverWait
        mock_driver = MagicMock()
        mock_wait_instance = MagicMock()
        mock_wait.return_value = mock_wait_instance
        
        # Call the wait_for_result method
        self.submitter.wait_for_result(mock_driver, "div.success")
        
        # Verify that WebDriverWait was instantiated with the correct arguments
        mock_wait.assert_called_once_with(mock_driver, 10)
        
        # Verify that until was called with a condition
        mock_wait_instance.until.assert_called_once()
    
    @patch('captcha_solver.submitter.WebDriverWait')
    def test_wait_for_result_with_custom_timeout(self, mock_wait):
        """Test the wait_for_result method with a custom timeout."""
        # Create a mock Selenium WebDriver and WebDriverWait
        mock_driver = MagicMock()
        mock_wait_instance = MagicMock()
        mock_wait.return_value = mock_wait_instance
        
        # Call the wait_for_result method with a custom timeout
        self.submitter.wait_for_result(mock_driver, "div.success", timeout=20)
        
        # Verify that WebDriverWait was instantiated with the custom timeout
        mock_wait.assert_called_once_with(mock_driver, 20)
        
        # Verify that until was called with a condition
        mock_wait_instance.until.assert_called_once()
    
    @patch('captcha_solver.submitter.WebDriverWait')
    def test_wait_for_result_timeout(self, mock_wait):
        """Test the wait_for_result method when it times out."""
        # Create a mock Selenium WebDriver and WebDriverWait
        mock_driver = MagicMock()
        mock_wait_instance = MagicMock()
        mock_wait_instance.until.side_effect = Exception("Timeout")
        mock_wait.return_value = mock_wait_instance
        
        # Call the wait_for_result method and expect an exception
        with self.assertRaises(Exception):
            self.submitter.wait_for_result(mock_driver, "div.success")
    
    def test_find_element(self):
        """Test the find_element method."""
        # Create a mock Selenium WebDriver
        mock_driver = MagicMock()
        mock_element = MagicMock()
        mock_driver.find_element.return_value = mock_element
        
        # Call the find_element method
        result = self.submitter.find_element(mock_driver, "div.success")
        
        # Verify that find_element was called with the correct selector
        mock_driver.find_element.assert_called_once_with("css selector", "div.success")
        
        # Verify the result is the mock element
        self.assertEqual(result, mock_element)
    
    def test_find_element_not_found(self):
        """Test the find_element method when the element is not found."""
        # Create a mock Selenium WebDriver
        mock_driver = MagicMock()
        mock_driver.find_element.side_effect = Exception("Element not found")
        
        # Call the find_element method and expect an exception
        with self.assertRaises(Exception):
            self.submitter.find_element(mock_driver, "div.success")
    
    def test_take_screenshot(self):
        """Test the take_screenshot method."""
        # Create a mock Selenium WebDriver
        mock_driver = MagicMock()
        mock_driver.get_screenshot_as_png.return_value = b"screenshot data"
        
        # Call the take_screenshot method
        result = self.submitter.take_screenshot(mock_driver)
        
        # Verify that get_screenshot_as_png was called
        mock_driver.get_screenshot_as_png.assert_called_once()
        
        # Verify the result is the screenshot data
        self.assertEqual(result, b"screenshot data")
    
    def test_take_screenshot_with_filename(self):
        """Test the take_screenshot method with a filename."""
        # Create a mock Selenium WebDriver
        mock_driver = MagicMock()
        mock_driver.get_screenshot_as_file.return_value = True
        
        # Call the take_screenshot method with a filename
        filename = os.path.join(self.test_dir, "screenshot.png")
        result = self.submitter.take_screenshot(mock_driver, filename=filename)
        
        # Verify that get_screenshot_as_file was called with the filename
        mock_driver.get_screenshot_as_file.assert_called_once_with(filename)
        
        # Verify the result is True
        self.assertTrue(result)
    
    def test_take_screenshot_with_element(self):
        """Test the take_screenshot method with an element."""
        # Create a mock Selenium WebDriver and WebElement
        mock_driver = MagicMock()
        mock_element = MagicMock()
        mock_element.screenshot_as_png = b"element screenshot data"
        
        # Call the take_screenshot method with an element
        result = self.submitter.take_screenshot(mock_driver, element=mock_element)
        
        # Verify that screenshot_as_png was accessed
        # This is a property, so we can't verify it was called
        
        # Verify the result is the element screenshot data
        self.assertEqual(result, b"element screenshot data")
    
    def test_take_screenshot_with_element_and_filename(self):
        """Test the take_screenshot method with an element and a filename."""
        # Create a mock Selenium WebDriver and WebElement
        mock_driver = MagicMock()
        mock_element = MagicMock()
        mock_element.screenshot_as_file.return_value = True
        
        # Call the take_screenshot method with an element and a filename
        filename = os.path.join(self.test_dir, "element_screenshot.png")
        result = self.submitter.take_screenshot(mock_driver, element=mock_element, filename=filename)
        
        # Verify that screenshot_as_file was called with the filename
        mock_element.screenshot_as_file.assert_called_once_with(filename)
        
        # Verify the result is True
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()