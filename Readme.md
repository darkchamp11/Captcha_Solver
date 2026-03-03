# CAPTCHA Solver Project

A comprehensive Python-based CAPTCHA solving toolkit that combines image preprocessing, OCR (Optical Character Recognition), and web automation to solve various types of text-based CAPTCHAs.

## ⚠️ Important Disclaimer

**This tool is intended for educational purposes, security research, and legitimate testing only.** 

- Use only on systems you own or have explicit permission to test
- Respect website terms of service and rate limits
- Do not use for malicious activities or to bypass security measures
- The developers are not responsible for misuse of this software

## 🚀 Features

- **Multi-source CAPTCHA extraction**: From files, URLs, and web elements
- **Advanced image preprocessing**: Noise reduction, enhancement, and optimization
- **Robust OCR engine**: Multiple Tesseract configurations for better accuracy
- **Web automation support**: Selenium integration for form submission
- **Batch processing**: Handle multiple CAPTCHAs efficiently
- **Comprehensive logging**: Detailed processing information and debugging
- **Flexible configuration**: Customizable settings for different CAPTCHA types
- **Performance monitoring**: Statistics and confidence scoring

## 📋 Requirements

### System Requirements
- Python 3.7 or higher
- Tesseract OCR engine
- Chrome/Firefox browser (for Selenium)

### Python Dependencies
See `requirements.txt` for the complete list. Key dependencies include:
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `Pillow` - Image processing
- `pytesseract` - OCR engine interface
- `selenium` - Web automation
- `opencv-python` - Advanced image processing
- `numpy` - Numerical operations

## 🛠️ Installation

### 1. Install Tesseract OCR

**Windows:**
```bash
# Download and install from: https://github.com/UB-Mannheim/tesseract/wiki
# Or using chocolatey:
choco install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install libtesseract-dev
```

**macOS:**
```bash
brew install tesseract
```

### 2. Clone and Setup Project
```bash
git clone <repository-url>
cd Captcha_Solver
pip install -r requirements.txt
```

### 3. Verify Installation
```python
from captcha_solver import CAPTCHASolver

solver = CAPTCHASolver()
print(solver.test_components())
```

## 📖 Quick Start

### Basic Usage

```python
from captcha_solver import CAPTCHASolver

# Initialize solver
solver = CAPTCHASolver()

# Solve from image file
result = solver.solve_from_file("captcha.png")
print(f"CAPTCHA solved: {result}")

# Solve from URL
result = solver.solve_from_url("https://example.com/captcha-page")
print(f"CAPTCHA solved: {result}")
```

### Advanced Usage with Custom Configuration

```python
from captcha_solver import CAPTCHASolver, Config

# Custom configuration
config = {
    "tesseract": {
        "config": "--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "timeout": 30
    },
    "preprocessing": {
        "steps": ["grayscale", "denoise", "threshold", "enhance"]
    },
    "ocr": {
        "confidence_threshold": 70
    }
}

solver = CAPTCHASolver(config=config)
result = solver.solve_from_file("difficult_captcha.png", save_processed=True)
print(f"Result: {result}, Confidence: {solver.get_confidence():.1f}%")
```

### Selenium Integration

```python
from selenium import webdriver
from captcha_solver import CAPTCHASolver, FormSubmitter

# Setup WebDriver
driver = webdriver.Chrome()
solver = CAPTCHASolver()
submitter = FormSubmitter(driver)

try:
    # Navigate to page with CAPTCHA
    driver.get("https://example.com/login")
    
    # Find CAPTCHA element
    captcha_element = driver.find_element("css selector", "img.captcha")
    
    # Solve CAPTCHA
    result = solver.solve_from_element(captcha_element, driver)
    
    # Submit form
    form_data = {
        "username": "your_username",
        "password": "your_password",
        "captcha": result
    }
    
    success = submitter.submit_form(form_data, "#login-form")
    print(f"Form submitted: {success}")
    
finally:
    driver.quit()
```

### Batch Processing

```python
from pathlib import Path
from captcha_solver import CAPTCHASolver

solver = CAPTCHASolver()

# Process all images in a directory
image_dir = Path("captcha_images")
image_paths = list(image_dir.glob("*.png"))

results = solver.solve_batch(image_paths, save_processed=True)

# Print results
for result in results:
    print(f"{result['path']}: {result['result']} ({result['confidence']:.1f}%)")

# Get statistics
stats = solver.get_statistics()
print(f"Success rate: {stats['success_rate']:.1f}%")
```

## 🏗️ Project Structure

```
Captcha_Solver/
├── captcha_solver/
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Configuration management
│   ├── solver.py            # Main solver class
│   ├── extractor.py         # CAPTCHA image extraction
│   ├── preprocessor.py      # Image preprocessing
│   ├── ocr.py              # OCR handling
│   ├── submitter.py        # Form submission
│   └── utils.py            # Utility functions
├── examples/
│   ├── basic_usage.py      # Basic examples
│   ├── advanced_config.py  # Advanced configuration
│   ├── selenium_example.py # Selenium integration
│   └── batch_processing.py # Batch processing
├── tests/
│   ├── test_solver.py      # Main solver tests
│   ├── test_preprocessor.py # Preprocessing tests
│   └── test_ocr.py         # OCR tests
├── docs/
│   ├── configuration.md    # Configuration guide
│   ├── preprocessing.md    # Preprocessing guide
│   └── troubleshooting.md  # Common issues
├── requirements.txt        # Python dependencies
├── setup.py               # Package setup
├── README.md              # This file
└── caotcha me.py          # Original implementation
```

## ⚙️ Configuration

The solver supports extensive configuration through YAML files or Python dictionaries:

```yaml
# config.yaml
tesseract:
  path: "/usr/bin/tesseract"  # Auto-detected if not specified
  config: "--psm 8 --oem 3"
  timeout: 30
  language: "eng"

preprocessing:
  steps:
    - "grayscale"
    - "denoise"
    - "threshold"
    - "enhance"
  
  grayscale:
    method: "weighted"  # "average", "weighted", "luminosity"
  
  denoise:
    method: "gaussian"  # "gaussian", "median", "bilateral"
    kernel_size: 3
  
  threshold:
    method: "adaptive"  # "binary", "adaptive", "otsu"
    block_size: 11
    c_value: 2

ocr:
  confidence_threshold: 60
  character_whitelist: "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
  multiple_configs: true

selenium:
  implicit_wait: 10
  page_load_timeout: 30
  screenshot_on_error: true

extraction:
  default_selectors:
    - "img[src*='captcha']"
    - ".captcha img"
    - "#captcha"
  timeout: 10
  retry_attempts: 3
```

## 🔧 Preprocessing Options

The image preprocessor supports various enhancement techniques:

- **Grayscale conversion**: Multiple algorithms for optimal contrast
- **Noise reduction**: Gaussian, median, and bilateral filtering
- **Thresholding**: Binary, adaptive, and Otsu methods
- **Morphological operations**: Opening, closing, erosion, dilation
- **Enhancement**: Contrast adjustment, sharpening, histogram equalization
- **Skew correction**: Automatic rotation correction
- **Character segmentation**: Individual character isolation

## 🎯 OCR Configuration

Tesseract OCR can be fine-tuned for different CAPTCHA types:

```python
# Numeric only CAPTCHAs
config = "--psm 8 -c tessedit_char_whitelist=0123456789"

# Alphanumeric CAPTCHAs
config = "--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

# Single word CAPTCHAs
config = "--psm 8 --oem 3"

# Multiple words
config = "--psm 6 --oem 3"
```

## 📊 Performance Monitoring

```python
solver = CAPTCHASolver()

# Process some CAPTCHAs...

# Get detailed statistics
stats = solver.get_statistics()
print(f"Total processed: {stats['total_processed']}")
print(f"Success rate: {stats['success_rate']:.1f}%")
print(f"Average confidence: {stats['average_confidence']:.1f}%")

# Get system information
info = solver.get_system_info()
print(f"Component tests: {info['component_tests']}")
```

## 🐛 Troubleshooting

### Common Issues

1. **Tesseract not found**
   ```
   TesseractNotFoundError: tesseract is not installed
   ```
   - Install Tesseract OCR and ensure it's in PATH
   - Or specify path in configuration

2. **Low accuracy**
   - Try different preprocessing steps
   - Adjust OCR configuration
   - Use character whitelisting
   - Check image quality and size

3. **Selenium WebDriver issues**
   - Update WebDriver to match browser version
   - Use webdriver-manager for automatic management
   - Check browser compatibility

### Debug Mode

```python
solver = CAPTCHASolver(log_level="DEBUG")
result = solver.solve_from_file("captcha.png", save_processed=True)

# Check processed image
processed_img = solver.get_processed_image()
processed_img.show()  # Display processed image

# Check confidence
print(f"Confidence: {solver.get_confidence():.1f}%")
```
## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCR engine
- [OpenCV](https://opencv.org/) - Computer vision library
- [Selenium](https://selenium.dev/) - Web automation framework
- [Pillow](https://pillow.readthedocs.io/) - Python imaging library

---

**Remember**: Use this tool responsibly and ethically. Always respect website terms of service and applicable laws.
