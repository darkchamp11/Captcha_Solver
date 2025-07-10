# CAPTCHA Solver User Guide

This guide provides detailed instructions on how to use the CAPTCHA Solver library for various use cases.

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Advanced Configuration](#advanced-configuration)
4. [Selenium Integration](#selenium-integration)
5. [Batch Processing](#batch-processing)
6. [Troubleshooting](#troubleshooting)

## Installation

### System Requirements

- Python 3.7 or higher
- Tesseract OCR 4.0 or higher

### Installing Tesseract OCR

#### Windows

1. Download the installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer and follow the instructions
3. Add the Tesseract installation directory to your PATH environment variable

#### macOS

```bash
brew install tesseract
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
```

### Installing the CAPTCHA Solver Package

```bash
pip install captcha-solver
```

Or install from source:

```bash
git clone https://github.com/yourusername/captcha-solver.git
cd captcha-solver
pip install -e .
```

## Basic Usage

### Solving a CAPTCHA from a File

```python
from captcha_solver.solver import CAPTCHASolver

# Initialize the solver
solver = CAPTCHASolver()

# Solve a CAPTCHA from a file
result = solver.solve_from_file("path/to/captcha.png")
print(f"CAPTCHA solution: {result}")
```

### Solving a CAPTCHA from a URL

```python
from captcha_solver.solver import CAPTCHASolver

# Initialize the solver
solver = CAPTCHASolver()

# Solve a CAPTCHA from a URL
result = solver.solve_from_url("https://example.com/captcha.png")
print(f"CAPTCHA solution: {result}")
```

### Using the Command Line Interface

```bash
# Solve a CAPTCHA from a file
captcha-solver solve --file path/to/captcha.png

# Solve a CAPTCHA from a URL
captcha-solver solve --url https://example.com/captcha.png

# Solve multiple CAPTCHAs in batch mode
captcha-solver batch --directory path/to/captchas --output results.csv
```

## Advanced Configuration

### Creating a Custom Configuration

```python
from captcha_solver.solver import CAPTCHASolver
from captcha_solver.config import Config

# Create a custom configuration
config = Config({
    "ocr": {
        "engine": "tesseract",
        "tesseract": {
            "config": "--psm 8 --oem 3",
            "lang": "eng"
        },
        "postprocess": True,
        "remove_spaces": True,
        "uppercase": True
    },
    "preprocessing": {
        "steps": ["grayscale", "threshold", "denoise"],
        "grayscale": {
            "method": "weighted"
        },
        "threshold": {
            "method": "adaptive",
            "block_size": 11,
            "c_value": 2
        },
        "denoise": {
            "method": "gaussian",
            "kernel_size": 3
        }
    }
})

# Initialize the solver with the custom configuration
solver = CAPTCHASolver(config)

# Solve a CAPTCHA
result = solver.solve_from_file("path/to/captcha.png")
print(f"CAPTCHA solution: {result}")
```

### Loading Configuration from a YAML File

```python
from captcha_solver.solver import CAPTCHASolver
from captcha_solver.config import Config

# Load configuration from a YAML file
config = Config("path/to/config.yaml")

# Initialize the solver with the loaded configuration
solver = CAPTCHASolver(config)

# Solve a CAPTCHA
result = solver.solve_from_file("path/to/captcha.png")
print(f"CAPTCHA solution: {result}")
```

Example YAML configuration file:

```yaml
ocr:
  engine: tesseract
  tesseract:
    config: --psm 8 --oem 3
    lang: eng
  postprocess: true
  remove_spaces: true
  uppercase: true

preprocessing:
  steps:
    - grayscale
    - threshold
    - denoise
  grayscale:
    method: weighted
  threshold:
    method: adaptive
    block_size: 11
    c_value: 2
  denoise:
    method: gaussian
    kernel_size: 3
```

### Optimizing for Different CAPTCHA Types

#### Numeric CAPTCHAs

```python
from captcha_solver.solver import CAPTCHASolver
from captcha_solver.config import Config

# Create a configuration optimized for numeric CAPTCHAs
config = Config({
    "ocr": {
        "engine": "tesseract",
        "tesseract": {
            "config": "--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789",
            "lang": "eng"
        }
    },
    "preprocessing": {
        "steps": ["grayscale", "threshold", "denoise"],
        "threshold": {
            "method": "binary",
            "threshold": 150
        }
    }
})

# Initialize the solver with the optimized configuration
solver = CAPTCHASolver(config)

# Solve a numeric CAPTCHA
result = solver.solve_from_file("path/to/numeric_captcha.png")
print(f"CAPTCHA solution: {result}")
```

#### Alphanumeric CAPTCHAs

```python
from captcha_solver.solver import CAPTCHASolver
from captcha_solver.config import Config

# Create a configuration optimized for alphanumeric CAPTCHAs
config = Config({
    "ocr": {
        "engine": "tesseract",
        "tesseract": {
            "config": "--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
            "lang": "eng"
        },
        "postprocess": True,
        "uppercase": True
    },
    "preprocessing": {
        "steps": ["grayscale", "threshold", "denoise", "morphology"],
        "threshold": {
            "method": "adaptive",
            "block_size": 11,
            "c_value": 2
        },
        "morphology": {
            "operation": "dilate",
            "kernel_size": 2
        }
    }
})

# Initialize the solver with the optimized configuration
solver = CAPTCHASolver(config)

# Solve an alphanumeric CAPTCHA
result = solver.solve_from_file("path/to/alphanumeric_captcha.png")
print(f"CAPTCHA solution: {result}")
```

## Selenium Integration

### Basic Form Submission

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from captcha_solver.solver import CAPTCHASolver

# Initialize the solver
solver = CAPTCHASolver()

# Set up Chrome WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Optional: run in headless mode
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

# Navigate to a webpage with a CAPTCHA
driver.get("https://example.com/form")

# Find the CAPTCHA element
captcha_element = solver.extractor.find_captcha_element(driver)

# Solve the CAPTCHA
solution = solver.solve_from_element(captcha_element)

# Submit the CAPTCHA solution
solver.submitter.submit_captcha_solution(driver, solution)

# Wait for the result
success = solver.submitter.wait_for_result(driver, "div.success")

if success:
    print("CAPTCHA solved successfully!")
else:
    print("Failed to solve CAPTCHA.")

# Close the browser
driver.quit()
```

### Advanced Form Handling

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from captcha_solver.solver import CAPTCHASolver

# Initialize the solver
solver = CAPTCHASolver()

# Set up Chrome WebDriver
chrome_options = Options()
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

# Navigate to a login form with a CAPTCHA
driver.get("https://example.com/login")

# Fill in the form fields
form_data = {
    "username": "testuser",
    "password": "testpass"
}
solver.submitter.fill_form_fields(driver, form_data)

# Find and solve the CAPTCHA
captcha_element = solver.extractor.find_captcha_element(driver)
solution = solver.solve_from_element(captcha_element)

# Submit the CAPTCHA solution
solver.submitter.submit_captcha_solution(driver, solution)

# Wait for the result with a custom timeout
success = solver.submitter.wait_for_result(
    driver, 
    "div.success", 
    timeout=15,
    failure_selector="div.error"
)

if success:
    print("Login successful!")
else:
    # Take a screenshot for debugging
    screenshot_path = "error_screenshot.png"
    solver.submitter.take_screenshot(driver, filename=screenshot_path)
    print(f"Login failed. Screenshot saved to {screenshot_path}")

# Close the browser
driver.quit()
```

## Batch Processing

### Processing Multiple Files

```python
from captcha_solver.solver import CAPTCHASolver
import os
import csv
from pathlib import Path

# Initialize the solver
solver = CAPTCHASolver()

# Directory containing CAPTCHA images
captcha_dir = Path("path/to/captchas")

# Output CSV file
output_file = "results.csv"

# Process all PNG files in the directory
results = []
for captcha_file in captcha_dir.glob("*.png"):
    try:
        # Solve the CAPTCHA
        solution = solver.solve_from_file(captcha_file)
        
        # Store the result
        results.append({
            "file": captcha_file.name,
            "solution": solution,
            "status": "success"
        })
        
        print(f"Solved {captcha_file.name}: {solution}")
    except Exception as e:
        # Handle errors
        results.append({
            "file": captcha_file.name,
            "solution": "",
            "status": f"error: {str(e)}"
        })
        
        print(f"Error solving {captcha_file.name}: {str(e)}")

# Write results to CSV
with open(output_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["file", "solution", "status"])
    writer.writeheader()
    writer.writerows(results)

print(f"Results saved to {output_file}")
```

### Parallel Processing

```python
from captcha_solver.solver import CAPTCHASolver
import os
import csv
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Function to solve a single CAPTCHA
def solve_captcha(file_path):
    try:
        # Initialize a solver for this thread
        solver = CAPTCHASolver()
        
        # Solve the CAPTCHA
        solution = solver.solve_from_file(file_path)
        
        return {
            "file": os.path.basename(file_path),
            "solution": solution,
            "status": "success"
        }
    except Exception as e:
        return {
            "file": os.path.basename(file_path),
            "solution": "",
            "status": f"error: {str(e)}"
        }

# Directory containing CAPTCHA images
captcha_dir = Path("path/to/captchas")

# Output CSV file
output_file = "results.csv"

# Get all PNG files in the directory
captcha_files = list(captcha_dir.glob("*.png"))

# Process files in parallel
results = []
with ThreadPoolExecutor(max_workers=4) as executor:
    # Submit all tasks
    future_to_file = {executor.submit(solve_captcha, str(file)): file for file in captcha_files}
    
    # Process results as they complete
    for future in as_completed(future_to_file):
        file = future_to_file[future]
        try:
            result = future.result()
            results.append(result)
            print(f"Solved {result['file']}: {result['solution']}")
        except Exception as e:
            print(f"Error processing {file.name}: {str(e)}")

# Write results to CSV
with open(output_file, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["file", "solution", "status"])
    writer.writeheader()
    writer.writerows(results)

print(f"Results saved to {output_file}")
```

## Troubleshooting

### Common Issues and Solutions

#### Poor OCR Accuracy

- **Issue**: The OCR engine is not accurately recognizing the CAPTCHA text.
- **Solution**: Try different preprocessing steps or adjust the OCR configuration.

```python
from captcha_solver.solver import CAPTCHASolver
from captcha_solver.config import Config

# Create a configuration with enhanced preprocessing
config = Config({
    "preprocessing": {
        "steps": ["grayscale", "threshold", "denoise", "morphology", "enhance"],
        "threshold": {
            "method": "adaptive",
            "block_size": 11,
            "c_value": 2
        },
        "enhance": {
            "method": "contrast",
            "factor": 2.0
        }
    },
    "ocr": {
        "engine": "tesseract",
        "tesseract": {
            "config": "--psm 8 --oem 3",
            "lang": "eng"
        }
    }
})

# Initialize the solver with the enhanced configuration
solver = CAPTCHASolver(config)

# Solve the CAPTCHA
result = solver.solve_from_file("path/to/captcha.png")
print(f"CAPTCHA solution: {result}")
```

#### Tesseract Not Found

- **Issue**: The solver cannot find the Tesseract OCR executable.
- **Solution**: Specify the path to the Tesseract executable in the configuration.

```python
from captcha_solver.solver import CAPTCHASolver
from captcha_solver.config import Config

# Create a configuration with the Tesseract path
config = Config({
    "ocr": {
        "engine": "tesseract",
        "tesseract": {
            "path": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"  # Windows path
            # "path": "/usr/bin/tesseract"  # Linux/macOS path
        }
    }
})

# Initialize the solver with the configuration
solver = CAPTCHASolver(config)

# Solve the CAPTCHA
result = solver.solve_from_file("path/to/captcha.png")
print(f"CAPTCHA solution: {result}")
```

#### Selenium Element Not Found

- **Issue**: The solver cannot find the CAPTCHA element on the webpage.
- **Solution**: Specify a custom CSS selector for the CAPTCHA element.

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from captcha_solver.solver import CAPTCHASolver
from captcha_solver.config import Config

# Create a configuration with custom selectors
config = Config({
    "extraction": {
        "selectors": {
            "captcha_img": "#custom-captcha-img",
            "captcha_input": "#custom-captcha-input"
        }
    },
    "submission": {
        "selectors": {
            "submit_button": "#custom-submit-button"
        }
    }
})

# Initialize the solver with the configuration
solver = CAPTCHASolver(config)

# Set up Chrome WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Navigate to a webpage with a CAPTCHA
driver.get("https://example.com/form")

# Find the CAPTCHA element with a custom selector
captcha_element = solver.extractor.find_captcha_element(
    driver, 
    selector="#custom-captcha-img"
)

# Solve the CAPTCHA
solution = solver.solve_from_element(captcha_element)

# Submit the CAPTCHA solution with custom selectors
solver.submitter.submit_captcha_solution(
    driver, 
    solution, 
    input_selector="#custom-captcha-input", 
    submit_selector="#custom-submit-button"
)

# Close the browser
driver.quit()
```

### Debugging

#### Enabling Debug Mode

```python
from captcha_solver.solver import CAPTCHASolver
from captcha_solver.config import Config
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create a configuration with debug mode enabled
config = Config({
    "debug": True,
    "debug_dir": "debug_output"
})

# Initialize the solver with debug mode
solver = CAPTCHASolver(config)

# Solve a CAPTCHA
result = solver.solve_from_file("path/to/captcha.png")
print(f"CAPTCHA solution: {result}")
```

#### Saving Intermediate Images

```python
from captcha_solver.solver import CAPTCHASolver
from captcha_solver.config import Config

# Create a configuration that saves intermediate images
config = Config({
    "debug": True,
    "debug_dir": "debug_output",
    "save_intermediate": True
})

# Initialize the solver with the configuration
solver = CAPTCHASolver(config)

# Solve a CAPTCHA
result = solver.solve_from_file("path/to/captcha.png")
print(f"CAPTCHA solution: {result}")
print(f"Intermediate images saved to {config.get('debug_dir')}")
```

#### Testing Individual Components

```python
from captcha_solver.solver import CAPTCHASolver
from PIL import Image

# Initialize the solver
solver = CAPTCHASolver()

# Load a CAPTCHA image
image = Image.open("path/to/captcha.png")

# Test the preprocessor
preprocessed_image = solver.preprocessor.preprocess_image(image)
preprocessed_image.save("preprocessed.png")

# Test the OCR handler
ocr_result = solver.ocr_handler.recognize_text(preprocessed_image)
print(f"OCR result: {ocr_result}")

# Test system information
system_info = solver.get_system_info()
print("System Information:")
for key, value in system_info.items():
    print(f"  {key}: {value}")
```