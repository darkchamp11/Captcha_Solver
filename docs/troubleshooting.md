# Troubleshooting Guide

This guide provides solutions to common issues you might encounter when using the CAPTCHA Solver library.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Tesseract OCR Issues](#tesseract-ocr-issues)
3. [Image Preprocessing Issues](#image-preprocessing-issues)
4. [OCR Accuracy Issues](#ocr-accuracy-issues)
5. [Selenium Integration Issues](#selenium-integration-issues)
6. [Performance Issues](#performance-issues)
7. [Error Messages](#error-messages)

## Installation Issues

### Package Installation Fails

**Problem**: Error when installing the CAPTCHA Solver package.

**Solution**:
1. Ensure you have the latest version of pip:
   ```bash
   python -m pip install --upgrade pip
   ```
2. Try installing in a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # macOS/Linux
   pip install captcha-solver
   ```
3. Check for conflicting dependencies and resolve them.

### Missing Dependencies

**Problem**: ImportError or ModuleNotFoundError when using the library.

**Solution**:
1. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```
2. If a specific dependency is causing issues, try installing it separately:
   ```bash
   pip install <dependency-name>
   ```

## Tesseract OCR Issues

### Tesseract Not Found

**Problem**: Error message indicating Tesseract OCR is not found.

**Solution**:
1. Ensure Tesseract OCR is installed on your system.
2. Verify the Tesseract executable path in your configuration:
   ```python
   from captcha_solver.config import Config
   
   config = Config()
   config.set("tesseract.executable_path", "/path/to/tesseract")
   ```
3. Add the Tesseract installation directory to your system PATH.

### Tesseract Language Data Not Found

**Problem**: Error message indicating Tesseract language data is not found.

**Solution**:
1. Ensure the required language data is installed.
2. Verify the Tesseract language data path in your configuration:
   ```python
   from captcha_solver.config import Config
   
   config = Config()
   config.set("tesseract.language", "eng")  # Use the appropriate language code
   ```

## Image Preprocessing Issues

### Poor Image Quality

**Problem**: The preprocessed image quality is poor, affecting OCR accuracy.

**Solution**:
1. Adjust the preprocessing parameters in your configuration:
   ```python
   from captcha_solver.config import Config
   
   config = Config()
   config.set("preprocessing.denoise.strength", 5)  # Adjust as needed
   config.set("preprocessing.threshold.method", "adaptive")  # Try different methods
   ```
2. Try different preprocessing steps or combinations.
3. Use the debug mode to visualize the preprocessing steps:
   ```python
   from captcha_solver.solver import CAPTCHASolver
   
   solver = CAPTCHASolver()
   solver.debug = True
   ```

### Image Not Recognized

**Problem**: The OCR engine fails to recognize any text in the image.

**Solution**:
1. Check if the image is properly loaded and preprocessed.
2. Try different preprocessing configurations.
3. Ensure the CAPTCHA image is not corrupted or empty.
4. Use the debug mode to visualize the preprocessing steps.

## OCR Accuracy Issues

### Low Recognition Accuracy

**Problem**: The OCR engine recognizes text, but with low accuracy.

**Solution**:
1. Adjust the OCR configuration:
   ```python
   from captcha_solver.config import Config
   
   config = Config()
   config.set("ocr.engine", "tesseract")  # Try different engines if available
   config.set("ocr.tesseract.config", "--psm 7 --oem 1")  # Adjust Tesseract parameters
   ```
2. Improve the preprocessing steps.
3. Train the OCR engine with similar CAPTCHA images if possible.
4. Try a different OCR engine or approach.

### Incorrect Character Recognition

**Problem**: Specific characters are consistently misrecognized.

**Solution**:
1. Use character whitelisting or blacklisting:
   ```python
   from captcha_solver.config import Config
   
   config = Config()
   config.set("ocr.tesseract.config", "--psm 7 --oem 1 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
   ```
2. Implement post-processing to correct common misrecognitions:
   ```python
   from captcha_solver.config import Config
   
   config = Config()
   config.set("ocr.post_processing.replacements", {"0": "O", "1": "I", "5": "S"})
   ```

## Selenium Integration Issues

### WebDriver Not Found

**Problem**: Error message indicating the WebDriver is not found.

**Solution**:
1. Ensure the WebDriver is installed and in your system PATH.
2. Specify the WebDriver path explicitly:
   ```python
   from selenium import webdriver
   
   driver = webdriver.Chrome(executable_path="/path/to/chromedriver")
   ```

### CAPTCHA Element Not Found

**Problem**: Error message indicating the CAPTCHA element is not found on the webpage.

**Solution**:
1. Verify the CSS selector for the CAPTCHA element:
   ```python
   from captcha_solver.config import Config
   
   config = Config()
   config.set("extraction.selenium.captcha_selector", "img.captcha")
   ```
2. Use the browser's developer tools to find the correct selector.
3. Ensure the webpage is fully loaded before searching for the element.
4. Try different methods to locate the element (CSS selector, XPath, etc.).

### Screenshot Capture Fails

**Problem**: Error when capturing a screenshot of the CAPTCHA element.

**Solution**:
1. Ensure the element is visible and not hidden.
2. Scroll the element into view before capturing the screenshot:
   ```python
   from selenium import webdriver
   from selenium.webdriver.common.action_chains import ActionChains
   
   driver = webdriver.Chrome()
   element = driver.find_element_by_css_selector("img.captcha")
   ActionChains(driver).move_to_element(element).perform()
   ```
3. Try a different method to extract the CAPTCHA image (e.g., "src" attribute instead of screenshot).

## Performance Issues

### Slow Processing

**Problem**: CAPTCHA solving is too slow.

**Solution**:
1. Optimize the preprocessing steps:
   ```python
   from captcha_solver.config import Config
   
   config = Config()
   config.set("preprocessing.steps", ["grayscale", "threshold"])  # Use fewer steps
   ```
2. Use a faster OCR engine or configuration.
3. Use batch processing for multiple CAPTCHAs:
   ```python
   from captcha_solver.solver import CAPTCHASolver
   
   solver = CAPTCHASolver()
   results = solver.solve_batch(["captcha1.png", "captcha2.png"], max_workers=4)
   ```
4. Increase the number of worker threads for batch processing.

### High Memory Usage

**Problem**: The library uses too much memory.

**Solution**:
1. Process images in smaller batches.
2. Reduce the image size or resolution if possible.
3. Close and release resources when not needed:
   ```python
   import gc
   
   # After using the solver
   solver = None
   gc.collect()
   ```

## Error Messages

### "Failed to initialize Tesseract OCR"

**Problem**: Tesseract OCR initialization fails.

**Solution**:
1. Ensure Tesseract OCR is properly installed.
2. Verify the Tesseract executable path.
3. Check if the required language data is installed.

### "Failed to preprocess image"

**Problem**: Image preprocessing fails.

**Solution**:
1. Check if the image is properly loaded.
2. Ensure the image format is supported.
3. Try different preprocessing configurations.

### "Failed to extract CAPTCHA from URL"

**Problem**: CAPTCHA extraction from a URL fails.

**Solution**:
1. Verify the URL is accessible and contains a valid image.
2. Check your network connection.
3. Ensure the URL is not protected or requires authentication.

### "Failed to submit CAPTCHA solution"

**Problem**: CAPTCHA solution submission fails.

**Solution**:
1. Verify the form input selectors.
2. Ensure the form is accessible and not protected by JavaScript.
3. Check if the form has changed or been updated.

## Additional Help

If you encounter issues not covered in this guide, please:

1. Check the [API Reference](api.md) for detailed information about the library's classes and methods.
2. Look for similar issues in the project's issue tracker.
3. Create a new issue with detailed information about the problem, including error messages, code snippets, and steps to reproduce the issue.
4. Join the community discussion forums or channels for help from other users.