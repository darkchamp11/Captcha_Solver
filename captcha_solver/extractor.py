"""CAPTCHA extraction module for CAPTCHA Solver.

This module handles extracting CAPTCHA images from web pages,
URLs, and Selenium WebElements.
"""

import requests
import base64
import re
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from typing import Optional, List, Dict, Any, Union
import logging
import time
from urllib.parse import urljoin, urlparse
from .utils import Timer, validate_url, retry_operation


class CAPTCHAExtractor:
    """CAPTCHA image extractor from various sources."""
    
    def __init__(self, config: dict):
        """Initialize CAPTCHA extractor with configuration.
        
        Args:
            config: Extraction configuration dictionary.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        
        # Set up session headers
        extraction_config = config.get("extraction", {})
        self.session.headers.update({
            'User-Agent': extraction_config.get(
                'user_agent', 
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            ),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        self.timeout = extraction_config.get('timeout', 30)
        self.retry_attempts = extraction_config.get('retry_attempts', 3)
    
    def extract_from_url(self, url: str, captcha_selectors: Optional[List[str]] = None) -> Optional[Image.Image]:
        """Extract CAPTCHA image from web page URL.
        
        Args:
            url: URL of the web page containing CAPTCHA.
            captcha_selectors: List of CSS selectors to find CAPTCHA images.
        
        Returns:
            PIL Image object or None if extraction fails.
        """
        if not validate_url(url):
            self.logger.error(f"Invalid URL: {url}")
            return None
        
        with Timer(f"CAPTCHA extraction from {url}") as timer:
            try:
                # Download page content
                response = retry_operation(
                    lambda: self.session.get(url, timeout=self.timeout),
                    max_attempts=self.retry_attempts,
                    exceptions=(requests.RequestException,)
                )
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find CAPTCHA elements
                captcha_elements = self.find_captcha_elements(soup, captcha_selectors)
                
                if not captcha_elements:
                    self.logger.warning("No CAPTCHA elements found on page")
                    return None
                
                # Try to extract image from each element
                for element in captcha_elements:
                    image = self._extract_image_from_element(element, url)
                    if image:
                        self.logger.info(f"CAPTCHA extracted successfully in {timer.elapsed:.3f}s")
                        return image
                
                self.logger.warning("Could not extract CAPTCHA image from any found elements")
                return None
                
            except Exception as e:
                self.logger.error(f"Failed to extract CAPTCHA from URL {url}: {e}")
                return None
    
    def extract_from_element(self, element, driver: Optional[webdriver.Chrome] = None) -> Optional[Image.Image]:
        """Extract CAPTCHA image from Selenium WebElement.
        
        Args:
            element: Selenium WebElement containing CAPTCHA image.
            driver: Selenium WebDriver instance (optional).
        
        Returns:
            PIL Image object or None if extraction fails.
        """
        try:
            with Timer("CAPTCHA extraction from WebElement") as timer:
                # Method 1: Screenshot of element
                try:
                    screenshot_bytes = element.screenshot_as_png
                    image = Image.open(BytesIO(screenshot_bytes))
                    self.logger.info(f"CAPTCHA extracted via screenshot in {timer.elapsed:.3f}s")
                    return image
                except Exception as e:
                    self.logger.debug(f"Screenshot method failed: {e}")
                
                # Method 2: Get src attribute and download
                try:
                    src = element.get_attribute('src')
                    if src:
                        image = self._download_image_from_src(src, driver.current_url if driver else None)
                        if image:
                            self.logger.info(f"CAPTCHA extracted via src download in {timer.elapsed:.3f}s")
                            return image
                except Exception as e:
                    self.logger.debug(f"Src download method failed: {e}")
                
                # Method 3: Get background image from CSS
                try:
                    style = element.get_attribute('style')
                    if style and 'background-image' in style:
                        url_match = re.search(r'url\(["\']?([^"\')]+)["\']?\)', style)
                        if url_match:
                            bg_url = url_match.group(1)
                            image = self._download_image_from_src(bg_url, driver.current_url if driver else None)
                            if image:
                                self.logger.info(f"CAPTCHA extracted via background image in {timer.elapsed:.3f}s")
                                return image
                except Exception as e:
                    self.logger.debug(f"Background image method failed: {e}")
                
                self.logger.warning("All extraction methods failed for WebElement")
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to extract CAPTCHA from WebElement: {e}")
            return None
    
    def download_image(self, image_url: str, base_url: Optional[str] = None) -> Optional[Image.Image]:
        """Download CAPTCHA image from URL.
        
        Args:
            image_url: URL of the CAPTCHA image.
            base_url: Base URL for resolving relative URLs.
        
        Returns:
            PIL Image object or None if download fails.
        """
        try:
            # Resolve relative URLs
            if base_url and not image_url.startswith(('http://', 'https://')):
                image_url = urljoin(base_url, image_url)
            
            return self._download_image_from_src(image_url, base_url)
            
        except Exception as e:
            self.logger.error(f"Failed to download image from {image_url}: {e}")
            return None
    
    def _download_image_from_src(self, src: str, base_url: Optional[str] = None) -> Optional[Image.Image]:
        """Download image from src attribute.
        
        Args:
            src: Image source (URL or data URI).
            base_url: Base URL for resolving relative URLs.
        
        Returns:
            PIL Image object or None if download fails.
        """
        try:
            # Handle data URIs
            if src.startswith('data:'):
                return self._decode_data_uri(src)
            
            # Handle regular URLs
            if base_url and not src.startswith(('http://', 'https://')):
                src = urljoin(base_url, src)
            
            response = retry_operation(
                lambda: self.session.get(src, timeout=self.timeout),
                max_attempts=self.retry_attempts,
                exceptions=(requests.RequestException,)
            )
            response.raise_for_status()
            
            # Verify content type
            content_type = response.headers.get('content-type', '')
            if not content_type.startswith('image/'):
                self.logger.warning(f"Unexpected content type: {content_type}")
            
            image = Image.open(BytesIO(response.content))
            return image
            
        except Exception as e:
            self.logger.error(f"Failed to download image from {src}: {e}")
            return None
    
    def _decode_data_uri(self, data_uri: str) -> Optional[Image.Image]:
        """Decode image from data URI.
        
        Args:
            data_uri: Data URI string.
        
        Returns:
            PIL Image object or None if decoding fails.
        """
        try:
            # Extract base64 data from data URI
            match = re.match(r'data:image/[^;]+;base64,(.+)', data_uri)
            if not match:
                self.logger.error("Invalid data URI format")
                return None
            
            base64_data = match.group(1)
            image_data = base64.b64decode(base64_data)
            image = Image.open(BytesIO(image_data))
            
            return image
            
        except Exception as e:
            self.logger.error(f"Failed to decode data URI: {e}")
            return None
    
    def find_captcha_elements(self, soup: BeautifulSoup, 
                            custom_selectors: Optional[List[str]] = None) -> List:
        """Find CAPTCHA elements in HTML soup.
        
        Args:
            soup: BeautifulSoup object of the HTML page.
            custom_selectors: Custom CSS selectors for CAPTCHA elements.
        
        Returns:
            List of found CAPTCHA elements.
        """
        captcha_elements = []
        
        # Default selectors for common CAPTCHA patterns
        default_selectors = [
            'img[src*="captcha"]',
            'img[alt*="captcha"]',
            'img[id*="captcha"]',
            'img[class*="captcha"]',
            'img[src*="verify"]',
            'img[alt*="verify"]',
            'img[src*="code"]',
            'canvas[id*="captcha"]',
            'canvas[class*="captcha"]',
            '.captcha img',
            '#captcha img',
            '.verification img',
            '#verification img',
        ]
        
        # Use custom selectors if provided, otherwise use defaults
        selectors = custom_selectors or default_selectors
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                captcha_elements.extend(elements)
            except Exception as e:
                self.logger.debug(f"Selector '{selector}' failed: {e}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_elements = []
        for element in captcha_elements:
            element_id = id(element)
            if element_id not in seen:
                seen.add(element_id)
                unique_elements.append(element)
        
        self.logger.info(f"Found {len(unique_elements)} potential CAPTCHA elements")
        return unique_elements
    
    def _extract_image_from_element(self, element, base_url: str) -> Optional[Image.Image]:
        """Extract image from HTML element.
        
        Args:
            element: BeautifulSoup element.
            base_url: Base URL for resolving relative URLs.
        
        Returns:
            PIL Image object or None if extraction fails.
        """
        try:
            # Try src attribute
            src = element.get('src')
            if src:
                return self._download_image_from_src(src, base_url)
            
            # Try data-src attribute (lazy loading)
            data_src = element.get('data-src')
            if data_src:
                return self._download_image_from_src(data_src, base_url)
            
            # Try background image in style
            style = element.get('style', '')
            if 'background-image' in style:
                url_match = re.search(r'url\(["\']?([^"\')]+)["\']?\)', style)
                if url_match:
                    bg_url = url_match.group(1)
                    return self._download_image_from_src(bg_url, base_url)
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Failed to extract image from element: {e}")
            return None
    
    def extract_with_selenium(self, url: str, captcha_selectors: Optional[List[str]] = None,
                            wait_time: int = 10) -> Optional[Image.Image]:
        """Extract CAPTCHA using Selenium WebDriver.
        
        Args:
            url: URL of the web page.
            captcha_selectors: CSS selectors for CAPTCHA elements.
            wait_time: Maximum time to wait for elements.
        
        Returns:
            PIL Image object or None if extraction fails.
        """
        driver = None
        try:
            # Set up WebDriver
            selenium_config = self.config.get("selenium", {})
            
            options = webdriver.ChromeOptions()
            if selenium_config.get("headless", True):
                options.add_argument("--headless")
            
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            
            window_size = selenium_config.get("window_size", [1920, 1080])
            options.add_argument(f"--window-size={window_size[0]},{window_size[1]}")
            
            driver = webdriver.Chrome(options=options)
            driver.set_page_load_timeout(self.timeout)
            
            # Navigate to page
            driver.get(url)
            
            # Wait for page to load
            time.sleep(2)
            
            # Find CAPTCHA elements
            selectors = captcha_selectors or [
                'img[src*="captcha"]',
                'img[alt*="captcha"]',
                'img[id*="captcha"]',
                'canvas[id*="captcha"]',
            ]
            
            for selector in selectors:
                try:
                    # Wait for element to be present
                    element = WebDriverWait(driver, wait_time).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    
                    # Extract image from element
                    image = self.extract_from_element(element, driver)
                    if image:
                        return image
                        
                except TimeoutException:
                    self.logger.debug(f"Timeout waiting for selector: {selector}")
                    continue
                except NoSuchElementException:
                    self.logger.debug(f"Element not found: {selector}")
                    continue
            
            self.logger.warning("No CAPTCHA elements found with Selenium")
            return None
            
        except Exception as e:
            self.logger.error(f"Selenium extraction failed: {e}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def get_extraction_info(self) -> Dict[str, Any]:
        """Get information about extraction capabilities.
        
        Returns:
            Dictionary with extraction information.
        """
        return {
            "timeout": self.timeout,
            "retry_attempts": self.retry_attempts,
            "user_agent": self.session.headers.get('User-Agent'),
            "supported_methods": [
                "URL extraction",
                "WebElement extraction", 
                "Direct image download",
                "Data URI decoding",
                "Selenium extraction"
            ],
            "config": self.config.get("extraction", {})
        }
    
    def close(self):
        """Close the requests session."""
        if self.session:
            self.session.close()