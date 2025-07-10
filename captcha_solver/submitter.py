"""Form submission module for CAPTCHA Solver.

This module handles submitting CAPTCHA solutions to web forms
using Selenium WebDriver automation.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementNotInteractableException,
    StaleElementReferenceException
)
from typing import Dict, Any, Optional, List, Union
import logging
import time
from .utils import Timer


class FormSubmitter:
    """Form submission handler for CAPTCHA solutions."""
    
    def __init__(self, driver: webdriver.Chrome, config: Optional[dict] = None):
        """Initialize form submitter with WebDriver.
        
        Args:
            driver: Selenium WebDriver instance.
            config: Optional configuration dictionary.
        """
        self.driver = driver
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.default_timeout = self.config.get("timeout", 10)
    
    def submit_captcha(self, captcha_text: str, form_selector: str, 
                      input_selector: Optional[str] = None,
                      submit_selector: Optional[str] = None) -> bool:
        """Submit CAPTCHA solution to form.
        
        Args:
            captcha_text: Solved CAPTCHA text.
            form_selector: CSS selector for the form element.
            input_selector: CSS selector for CAPTCHA input field.
            submit_selector: CSS selector for submit button.
        
        Returns:
            True if submission successful, False otherwise.
        """
        try:
            with Timer("CAPTCHA form submission") as timer:
                # Find form element
                form_element = self._find_element(form_selector)
                if not form_element:
                    self.logger.error(f"Form not found: {form_selector}")
                    return False
                
                # Find CAPTCHA input field
                if input_selector:
                    input_element = self._find_element(input_selector, parent=form_element)
                else:
                    input_element = self._find_captcha_input(form_element)
                
                if not input_element:
                    self.logger.error("CAPTCHA input field not found")
                    return False
                
                # Clear and fill input field
                self._clear_and_fill_input(input_element, captcha_text)
                
                # Submit form
                success = self._submit_form(form_element, submit_selector)
                
                if success:
                    self.logger.info(f"CAPTCHA submitted successfully in {timer.elapsed:.3f}s")
                else:
                    self.logger.error("Form submission failed")
                
                return success
                
        except Exception as e:
            self.logger.error(f"CAPTCHA submission failed: {e}")
            return False
    
    def fill_form_fields(self, field_data: Dict[str, str]) -> bool:
        """Fill additional form fields.
        
        Args:
            field_data: Dictionary mapping field selectors to values.
        
        Returns:
            True if all fields filled successfully, False otherwise.
        """
        try:
            with Timer("Form field filling") as timer:
                success_count = 0
                total_fields = len(field_data)
                
                for selector, value in field_data.items():
                    try:
                        element = self._find_element(selector)
                        if element:
                            self._clear_and_fill_input(element, value)
                            success_count += 1
                            self.logger.debug(f"Filled field {selector} with value: {value}")
                        else:
                            self.logger.warning(f"Field not found: {selector}")
                    except Exception as e:
                        self.logger.error(f"Failed to fill field {selector}: {e}")
                
                success = success_count == total_fields
                self.logger.info(f"Filled {success_count}/{total_fields} fields in {timer.elapsed:.3f}s")
                return success
                
        except Exception as e:
            self.logger.error(f"Form field filling failed: {e}")
            return False
    
    def wait_for_result(self, timeout: int = 10, success_indicators: Optional[List[str]] = None,
                       error_indicators: Optional[List[str]] = None) -> Dict[str, Any]:
        """Wait for form submission result.
        
        Args:
            timeout: Maximum time to wait for result.
            success_indicators: CSS selectors indicating successful submission.
            error_indicators: CSS selectors indicating submission errors.
        
        Returns:
            Dictionary with result information.
        """
        try:
            with Timer("Waiting for submission result") as timer:
                start_time = time.time()
                
                # Default indicators
                default_success = [
                    '.success', '.alert-success', '.message-success',
                    '[class*="success"]', '[id*="success"]'
                ]
                default_error = [
                    '.error', '.alert-error', '.message-error', '.alert-danger',
                    '[class*="error"]', '[id*="error"]', '[class*="invalid"]'
                ]
                
                success_selectors = success_indicators or default_success
                error_selectors = error_indicators or default_error
                
                while time.time() - start_time < timeout:
                    # Check for success indicators
                    for selector in success_selectors:
                        try:
                            element = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if element.is_displayed():
                                return {
                                    "status": "success",
                                    "message": element.text.strip(),
                                    "element": selector,
                                    "time_taken": timer.elapsed
                                }
                        except NoSuchElementException:
                            continue
                    
                    # Check for error indicators
                    for selector in error_selectors:
                        try:
                            element = self.driver.find_element(By.CSS_SELECTOR, selector)
                            if element.is_displayed():
                                return {
                                    "status": "error",
                                    "message": element.text.strip(),
                                    "element": selector,
                                    "time_taken": timer.elapsed
                                }
                        except NoSuchElementException:
                            continue
                    
                    # Check if URL changed (might indicate redirect)
                    current_url = self.driver.current_url
                    if hasattr(self, '_initial_url') and current_url != self._initial_url:
                        return {
                            "status": "redirect",
                            "message": f"Redirected to: {current_url}",
                            "url": current_url,
                            "time_taken": timer.elapsed
                        }
                    
                    time.sleep(0.5)  # Wait before next check
                
                # Timeout reached
                return {
                    "status": "timeout",
                    "message": f"No result detected within {timeout} seconds",
                    "time_taken": timer.elapsed
                }
                
        except Exception as e:
            self.logger.error(f"Error waiting for result: {e}")
            return {
                "status": "error",
                "message": f"Exception while waiting: {str(e)}",
                "time_taken": 0
            }
    
    def _find_element(self, selector: str, timeout: Optional[int] = None, 
                     parent=None) -> Optional[Any]:
        """Find element by CSS selector with wait.
        
        Args:
            selector: CSS selector string.
            timeout: Maximum time to wait for element.
            parent: Parent element to search within.
        
        Returns:
            WebElement or None if not found.
        """
        try:
            wait_time = timeout or self.default_timeout
            search_context = parent or self.driver
            
            if hasattr(search_context, 'find_element'):
                # Direct element search
                element = WebDriverWait(search_context, wait_time).until(
                    lambda x: x.find_element(By.CSS_SELECTOR, selector)
                )
            else:
                # WebDriver search
                element = WebDriverWait(self.driver, wait_time).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
            
            return element
            
        except TimeoutException:
            self.logger.debug(f"Element not found within {wait_time}s: {selector}")
            return None
        except Exception as e:
            self.logger.error(f"Error finding element {selector}: {e}")
            return None
    
    def _find_captcha_input(self, form_element) -> Optional[Any]:
        """Find CAPTCHA input field within form.
        
        Args:
            form_element: Form WebElement to search within.
        
        Returns:
            Input WebElement or None if not found.
        """
        # Common selectors for CAPTCHA input fields
        captcha_selectors = [
            'input[name*="captcha"]',
            'input[id*="captcha"]',
            'input[class*="captcha"]',
            'input[name*="verify"]',
            'input[id*="verify"]',
            'input[name*="code"]',
            'input[id*="code"]',
            'input[type="text"]',  # Fallback to any text input
        ]
        
        for selector in captcha_selectors:
            try:
                element = form_element.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed() and element.is_enabled():
                    self.logger.debug(f"Found CAPTCHA input: {selector}")
                    return element
            except NoSuchElementException:
                continue
        
        self.logger.warning("No CAPTCHA input field found in form")
        return None
    
    def _clear_and_fill_input(self, element, value: str) -> bool:
        """Clear input field and fill with value.
        
        Args:
            element: Input WebElement.
            value: Value to fill.
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(0.5)
            
            # Clear field using multiple methods
            element.clear()
            element.send_keys(Keys.CONTROL + "a")  # Select all
            element.send_keys(Keys.DELETE)  # Delete selected
            
            # Fill with new value
            element.send_keys(value)
            
            # Verify value was set
            actual_value = element.get_attribute('value')
            if actual_value != value:
                self.logger.warning(f"Input value mismatch. Expected: '{value}', Got: '{actual_value}'")
                # Try again with JavaScript
                self.driver.execute_script("arguments[0].value = arguments[1];", element, value)
                # Trigger change event
                self.driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", element)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to fill input: {e}")
            return False
    
    def _submit_form(self, form_element, submit_selector: Optional[str] = None) -> bool:
        """Submit form using button or form submission.
        
        Args:
            form_element: Form WebElement.
            submit_selector: CSS selector for submit button.
        
        Returns:
            True if submission successful, False otherwise.
        """
        try:
            # Store initial URL for redirect detection
            self._initial_url = self.driver.current_url
            
            if submit_selector:
                # Find and click submit button
                submit_button = self._find_element(submit_selector)
                if submit_button:
                    self._click_element(submit_button)
                    return True
                else:
                    self.logger.warning(f"Submit button not found: {submit_selector}")
            
            # Try to find submit button within form
            submit_selectors = [
                'input[type="submit"]',
                'button[type="submit"]',
                'button:contains("Submit")',
                'input[value*="Submit"]',
                'button',  # Fallback to any button
            ]
            
            for selector in submit_selectors:
                try:
                    button = form_element.find_element(By.CSS_SELECTOR, selector)
                    if button.is_displayed() and button.is_enabled():
                        self._click_element(button)
                        return True
                except NoSuchElementException:
                    continue
            
            # Fallback: submit form directly
            self.logger.debug("Submitting form directly")
            form_element.submit()
            return True
            
        except Exception as e:
            self.logger.error(f"Form submission failed: {e}")
            return False
    
    def _click_element(self, element) -> bool:
        """Click element with multiple fallback methods.
        
        Args:
            element: WebElement to click.
        
        Returns:
            True if click successful, False otherwise.
        """
        try:
            # Method 1: Regular click
            try:
                element.click()
                return True
            except ElementNotInteractableException:
                pass
            
            # Method 2: JavaScript click
            try:
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except Exception:
                pass
            
            # Method 3: ActionChains click
            try:
                ActionChains(self.driver).move_to_element(element).click().perform()
                return True
            except Exception:
                pass
            
            self.logger.error("All click methods failed")
            return False
            
        except Exception as e:
            self.logger.error(f"Click failed: {e}")
            return False
    
    def get_form_info(self, form_selector: str) -> Dict[str, Any]:
        """Get information about form structure.
        
        Args:
            form_selector: CSS selector for form.
        
        Returns:
            Dictionary with form information.
        """
        try:
            form_element = self._find_element(form_selector)
            if not form_element:
                return {"error": "Form not found"}
            
            # Find all input fields
            inputs = form_element.find_elements(By.TAG_NAME, "input")
            buttons = form_element.find_elements(By.TAG_NAME, "button")
            
            input_info = []
            for inp in inputs:
                input_info.append({
                    "type": inp.get_attribute("type"),
                    "name": inp.get_attribute("name"),
                    "id": inp.get_attribute("id"),
                    "class": inp.get_attribute("class"),
                    "placeholder": inp.get_attribute("placeholder"),
                    "required": inp.get_attribute("required") is not None,
                    "visible": inp.is_displayed(),
                    "enabled": inp.is_enabled()
                })
            
            button_info = []
            for btn in buttons:
                button_info.append({
                    "type": btn.get_attribute("type"),
                    "text": btn.text,
                    "id": btn.get_attribute("id"),
                    "class": btn.get_attribute("class"),
                    "visible": btn.is_displayed(),
                    "enabled": btn.is_enabled()
                })
            
            return {
                "form_action": form_element.get_attribute("action"),
                "form_method": form_element.get_attribute("method"),
                "inputs": input_info,
                "buttons": button_info,
                "total_inputs": len(inputs),
                "total_buttons": len(buttons)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get form info: {e}")
            return {"error": str(e)}
    
    def take_screenshot(self, filename: str) -> bool:
        """Take screenshot for debugging.
        
        Args:
            filename: Path to save screenshot.
        
        Returns:
            True if screenshot saved successfully.
        """
        try:
            self.driver.save_screenshot(filename)
            self.logger.info(f"Screenshot saved: {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return False