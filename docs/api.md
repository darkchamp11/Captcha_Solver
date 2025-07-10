# API Reference

This document provides detailed information about the CAPTCHA Solver API, including classes, methods, and configuration options.

## Table of Contents

1. [CAPTCHASolver](#captchasolver)
2. [Config](#config)
3. [CAPTCHAExtractor](#captchaextractor)
4. [ImagePreprocessor](#imagepreprocessor)
5. [OCRHandler](#ocrhandler)
6. [FormSubmitter](#formsubmitter)

## CAPTCHASolver

The main class that orchestrates the CAPTCHA solving process.

### Constructor

```python
CAPTCHASolver(config=None)
```

**Parameters:**
- `config` (optional): A `Config` object or a path to a YAML configuration file. If not provided, default configuration is used.

### Methods

#### solve_from_file

```python
solve_from_file(file_path)
```

Solves a CAPTCHA from an image file.

**Parameters:**
- `file_path`: Path to the CAPTCHA image file.

**Returns:**
- The recognized CAPTCHA text.

**Example:**
```python
from captcha_solver.solver import CAPTCHASolver

solver = CAPTCHASolver()
result = solver.solve_from_file("captcha.png")
print(f"CAPTCHA solution: {result}")
```

#### solve_from_url

```python
solve_from_url(url)
```

Solves a CAPTCHA from a URL.

**Parameters:**
- `url`: URL of the CAPTCHA image.

**Returns:**
- The recognized CAPTCHA text.

**Example:**
```python
from captcha_solver.solver import CAPTCHASolver

solver = CAPTCHASolver()
result = solver.solve_from_url("https://example.com/captcha.png")
print(f"CAPTCHA solution: {result}")
```

#### solve_from_element

```python
solve_from_element(element, method="screenshot")
```

Solves a CAPTCHA from a Selenium WebElement.

**Parameters:**
- `element`: A Selenium WebElement containing the CAPTCHA image.
- `method` (optional): The method to extract the image from the element. Can be "screenshot", "src", or "background". Default is "screenshot".

**Returns:**
- The recognized CAPTCHA text.

**Example:**
```python
from selenium import webdriver
from captcha_solver.solver import CAPTCHASolver

driver = webdriver.Chrome()
driver.get("https://example.com/form")

solver = CAPTCHASolver()
captcha_element = driver.find_element_by_css_selector("img.captcha")
result = solver.solve_from_element(captcha_element)
print(f"CAPTCHA solution: {result}")
```

#### solve_from_webpage

```python
solve_from_webpage(url, selector=None)
```

Solves a CAPTCHA from a webpage by extracting the CAPTCHA image.

**Parameters:**
- `url`: URL of the webpage containing the CAPTCHA.
- `selector` (optional): CSS selector for the CAPTCHA image element. If not provided, the default selector from the configuration is used.

**Returns:**
- The recognized CAPTCHA text.

**Example:**
```python
from captcha_solver.solver import CAPTCHASolver

solver = CAPTCHASolver()
result = solver.solve_from_webpage("https://example.com/form", selector="img.captcha")
print(f"CAPTCHA solution: {result}")
```

#### solve_batch

```python
solve_batch(file_paths, max_workers=None)
```

Solves multiple CAPTCHAs in batch mode.

**Parameters:**
- `file_paths`: A list of paths to CAPTCHA image files.
- `max_workers` (optional): Maximum number of worker threads for parallel processing. If not provided, uses the default from the configuration.

**Returns:**
- A list of dictionaries containing the file path, solution, and status for each CAPTCHA.

**Example:**
```python
from captcha_solver.solver import CAPTCHASolver
from pathlib import Path

solver = CAPTCHASolver()
captcha_dir = Path("captchas")
file_paths = list(captcha_dir.glob("*.png"))
results = solver.solve_batch(file_paths, max_workers=4)

for result in results:
    print(f"File: {result['file']}, Solution: {result['solution']}, Status: {result['status']}")
```

#### get_statistics

```python
get_statistics()
```

Returns statistics about the CAPTCHA solving process.

**Returns:**
- A dictionary containing statistics such as the number of CAPTCHAs solved, success rate, average processing time, etc.

**Example:**
```python
from captcha_solver.solver import CAPTCHASolver

solver = CAPTCHASolver()
solver.solve_from_file("captcha1.png")
solver.solve_from_file("captcha2.png")

stats = solver.get_statistics()
print(f"Success rate: {stats['success_rate']}%")
print(f"Average processing time: {stats['avg_processing_time']} ms")
```

#### get_system_info

```python
get_system_info()
```

Returns information about the system and installed dependencies.

**Returns:**
- A dictionary containing system information such as the Python version, Tesseract version, OpenCV version, etc.

**Example:**
```python
from captcha_solver.solver import CAPTCHASolver

solver = CAPTCHASolver()
system_info = solver.get_system_info()

for key, value in system_info.items():
    print(f"{key}: {value}")
```

#### test_components

```python
test_components()
```

Tests the individual components of the CAPTCHA solver.

**Returns:**
- A dictionary containing the test results for each component.

**Example:**
```python
from captcha_solver.solver import CAPTCHASolver

solver = CAPTCHASolver()
test_results = solver.test_components()

for component, result in test_results.items():
    print(f"{component}: {'Success' if result else 'Failure'}")
```

## Config

A class for managing configuration settings.

### Constructor

```python
Config(config=None)
```

**Parameters:**
- `config` (optional): A dictionary, a path to a YAML configuration file, or another `Config` object. If not provided, default configuration is used.

### Methods

#### get

```python
get(key, default=None)
```

Gets a configuration value by key.

**Parameters:**
- `key`: The configuration key in dot notation (e.g., "ocr.engine").
- `default` (optional): The default value to return if the key is not found.

**Returns:**
- The configuration value, or the default value if the key is not found.

**Example:**
```python
from captcha_solver.config import Config

config = Config()
engine = config.get("ocr.engine")
print(f"OCR engine: {engine}")
```

#### set

```python
set(key, value)
```

Sets a configuration value by key.

**Parameters:**
- `key`: The configuration key in dot notation (e.g., "ocr.engine").
- `value`: The value to set.

**Example:**
```python
from captcha_solver.config import Config

config = Config()
config.set("ocr.engine", "custom")
config.set("ocr.custom.module", "my_ocr_module")
```

#### update

```python
update(config)
```

Updates the configuration with values from another configuration.

**Parameters:**
- `config`: A dictionary, a path to a YAML configuration file, or another `Config` object.

**Example:**
```python
from captcha_solver.config import Config

config = Config()
config.update({
    "ocr": {
        "engine": "custom",
        "custom": {
            "module": "my_ocr_module"
        }
    }
})
```

#### save

```python
save(file_path)
```

Saves the configuration to a YAML file.

**Parameters:**
- `file_path`: The path to save the configuration file.

**Example:**
```python
from captcha_solver.config import Config

config = Config()
config.set("ocr.engine", "custom")
config.save("config.yaml")
```

#### validate

```python
validate()
```

Validates the configuration.

**Returns:**
- `True` if the configuration is valid, `False` otherwise.

**Example:**
```python
from captcha_solver.config import Config

config = Config()
if config.validate():
    print("Configuration is valid")
else:
    print("Configuration is invalid")
```

#### to_dict

```python
to_dict()
```

Converts the configuration to a dictionary.

**Returns:**
- A dictionary representation of the configuration.

**Example:**
```python
from captcha_solver.config import Config

config = Config()
config_dict = config.to_dict()
print(config_dict)
```

#### get_default_config

```python
get_default_config()
```

Returns the default configuration.

**Returns:**
- A dictionary containing the default configuration.

**Example:**
```python
from captcha_solver.config import Config

default_config = Config.get_default_config()
print(default_config)
```

## CAPTCHAExtractor

A class for extracting CAPTCHA images from various sources.

### Constructor

```python
CAPTCHAExtractor(config=None)
```

**Parameters:**
- `config` (optional): A `Config` object or a path to a YAML configuration file. If not provided, default configuration is used.

### Methods

#### extract_from_url

```python
extract_from_url(url)
```

Extracts a CAPTCHA image from a URL.

**Parameters:**
- `url`: URL of the CAPTCHA image.

**Returns:**
- A PIL Image object containing the CAPTCHA image.

**Example:**
```python
from captcha_solver.extractor import CAPTCHAExtractor

extractor = CAPTCHAExtractor()
image = extractor.extract_from_url("https://example.com/captcha.png")
image.save("captcha.png")
```

#### extract_from_webpage

```python
extract_from_webpage(url, selector=None)
```

Extracts a CAPTCHA image from a webpage.

**Parameters:**
- `url`: URL of the webpage containing the CAPTCHA.
- `selector` (optional): CSS selector for the CAPTCHA image element. If not provided, the default selector from the configuration is used.

**Returns:**
- A PIL Image object containing the CAPTCHA image.

**Example:**
```python
from captcha_solver.extractor import CAPTCHAExtractor

extractor = CAPTCHAExtractor()
image = extractor.extract_from_webpage("https://example.com/form", selector="img.captcha")
image.save("captcha.png")
```

#### extract_from_element

```python
extract_from_element(element, method="screenshot")
```

Extracts a CAPTCHA image from a Selenium WebElement.

**Parameters:**
- `element`: A Selenium WebElement containing the CAPTCHA image.
- `method` (optional): The method to extract the image from the element. Can be "screenshot", "src", or "background". Default is "screenshot".

**Returns:**
- A PIL Image object containing the CAPTCHA image.

**Example:**
```python
from selenium import webdriver
from captcha_solver.extractor import CAPTCHAExtractor

driver = webdriver.Chrome()
driver.get("https://example.com/form")

extractor = CAPTCHAExtractor()
captcha_element = driver.find_element_by_css_selector("img.captcha")
image = extractor.extract_from_element(captcha_element)
image.save("captcha.png")
```

#### find_captcha_element

```python
find_captcha_element(driver, selector=None)
```

Finds a CAPTCHA element on a webpage.

**Parameters:**
- `driver`: A Selenium WebDriver instance.
- `selector` (optional): CSS selector for the CAPTCHA image element. If not provided, the default selector from the configuration is used.

**Returns:**
- A Selenium WebElement containing the CAPTCHA image.

**Example:**
```python
from selenium import webdriver
from captcha_solver.extractor import CAPTCHAExtractor

driver = webdriver.Chrome()
driver.get("https://example.com/form")

extractor = CAPTCHAExtractor()
captcha_element = extractor.find_captcha_element(driver)
image = extractor.extract_from_element(captcha_element)
image.save("captcha.png")
```

#### extract_with_selenium

```python
extract_with_selenium(url, selector=None)
```

Extracts a CAPTCHA image from a webpage using Selenium.

**Parameters:**
- `url`: URL of the webpage containing the CAPTCHA.
- `selector` (optional): CSS selector for the CAPTCHA image element. If not provided, the default selector from the configuration is used.

**Returns:**
- A PIL Image object containing the CAPTCHA image.

**Example:**
```python
from captcha_solver.extractor import CAPTCHAExtractor

extractor = CAPTCHAExtractor()
image = extractor.extract_with_selenium("https://example.com/form", selector="img.captcha")
image.save("captcha.png")
```

## ImagePreprocessor

A class for preprocessing CAPTCHA images to improve OCR accuracy.

### Constructor

```python
ImagePreprocessor(config=None)
```

**Parameters:**
- `config` (optional): A `Config` object or a path to a YAML configuration file. If not provided, default configuration is used.

### Methods

#### preprocess_image

```python
preprocess_image(image)
```

Preprocesses a CAPTCHA image to improve OCR accuracy.

**Parameters:**
- `image`: A PIL Image object containing the CAPTCHA image.

**Returns:**
- A preprocessed PIL Image object.

**Example:**
```python
from PIL import Image
from captcha_solver.preprocessor import ImagePreprocessor

image = Image.open("captcha.png")
preprocessor = ImagePreprocessor()
preprocessed_image = preprocessor.preprocess_image(image)
preprocessed_image.save("preprocessed.png")
```

## OCRHandler

A class for recognizing text in CAPTCHA images using OCR.

### Constructor

```python
OCRHandler(config=None)
```

**Parameters:**
- `config` (optional): A `Config` object or a path to a YAML configuration file. If not provided, default configuration is used.

### Methods

#### recognize_text

```python
recognize_text(image)
```

Recognizes text in a CAPTCHA image using OCR.

**Parameters:**
- `image`: A PIL Image object containing the CAPTCHA image.

**Returns:**
- The recognized text.

**Example:**
```python
from PIL import Image
from captcha_solver.ocr import OCRHandler

image = Image.open("captcha.png")
ocr_handler = OCRHandler()
text = ocr_handler.recognize_text(image)
print(f"Recognized text: {text}")
```

## FormSubmitter

A class for submitting CAPTCHA solutions to web forms.

### Constructor

```python
FormSubmitter(config=None)
```

**Parameters:**
- `config` (optional): A `Config` object or a path to a YAML configuration file. If not provided, default configuration is used.

### Methods

#### submit_captcha_solution

```python
submit_captcha_solution(driver, solution, input_selector=None, submit_selector=None)
```

Submits a CAPTCHA solution to a web form.

**Parameters:**
- `driver`: A Selenium WebDriver instance.
- `solution`: The CAPTCHA solution to submit.
- `input_selector` (optional): CSS selector for the CAPTCHA input field. If not provided, the default selector from the configuration is used.
- `submit_selector` (optional): CSS selector for the submit button. If not provided, the default selector from the configuration is used.

**Example:**
```python
from selenium import webdriver
from captcha_solver.submitter import FormSubmitter

driver = webdriver.Chrome()
driver.get("https://example.com/form")

submitter = FormSubmitter()
submitter.submit_captcha_solution(driver, "ABC123")
```

#### fill_form_fields

```python
fill_form_fields(driver, fields)
```

Fills form fields with the provided values.

**Parameters:**
- `driver`: A Selenium WebDriver instance.
- `fields`: A dictionary mapping field names to values or dictionaries with "value" and "selector" keys.

**Example:**
```python
from selenium import webdriver
from captcha_solver.submitter import FormSubmitter

driver = webdriver.Chrome()
driver.get("https://example.com/form")

submitter = FormSubmitter()
submitter.fill_form_fields(driver, {
    "username": "testuser",
    "password": "testpass",
    "email": {
        "value": "test@example.com",
        "selector": "#email-field"
    }
})
```

#### wait_for_result

```python
wait_for_result(driver, success_selector, failure_selector=None, timeout=None)
```

Waits for the result of the form submission.

**Parameters:**
- `driver`: A Selenium WebDriver instance.
- `success_selector`: CSS selector for the success element.
- `failure_selector` (optional): CSS selector for the failure element.
- `timeout` (optional): Timeout in seconds. If not provided, the default timeout from the configuration is used.

**Returns:**
- `True` if the success element is found, `False` if the failure element is found, or `None` if the timeout is reached.

**Example:**
```python
from selenium import webdriver
from captcha_solver.submitter import FormSubmitter

driver = webdriver.Chrome()
driver.get("https://example.com/form")

submitter = FormSubmitter()
submitter.submit_captcha_solution(driver, "ABC123")
result = submitter.wait_for_result(driver, "div.success", failure_selector="div.error", timeout=10)

if result:
    print("Form submitted successfully")
else:
    print("Form submission failed")
```

#### find_element

```python
find_element(driver, selector)
```

Finds an element on a webpage.

**Parameters:**
- `driver`: A Selenium WebDriver instance.
- `selector`: CSS selector for the element.

**Returns:**
- A Selenium WebElement.

**Example:**
```python
from selenium import webdriver
from captcha_solver.submitter import FormSubmitter

driver = webdriver.Chrome()
driver.get("https://example.com/form")

submitter = FormSubmitter()
element = submitter.find_element(driver, "input[name='username']")
element.send_keys("testuser")
```

#### take_screenshot

```python
take_screenshot(driver, element=None, filename=None)
```

Takes a screenshot of the webpage or a specific element.

**Parameters:**
- `driver`: A Selenium WebDriver instance.
- `element` (optional): A Selenium WebElement to take a screenshot of. If not provided, takes a screenshot of the entire page.
- `filename` (optional): The filename to save the screenshot to. If not provided, returns the screenshot as bytes.

**Returns:**
- The screenshot as bytes if `filename` is not provided, otherwise `True` if the screenshot was saved successfully.

**Example:**
```python
from selenium import webdriver
from captcha_solver.submitter import FormSubmitter

driver = webdriver.Chrome()
driver.get("https://example.com/form")

submitter = FormSubmitter()

# Take a screenshot of the entire page
submitter.take_screenshot(driver, filename="page.png")

# Take a screenshot of a specific element
element = driver.find_element_by_css_selector("div.form")
submitter.take_screenshot(driver, element=element, filename="form.png")
```