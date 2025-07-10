"""CAPTCHA Solver Package

A comprehensive Python package for solving text-based CAPTCHA challenges
using computer vision and OCR techniques.

This package is intended for educational and research purposes only.
Users must ensure compliance with applicable laws and website terms of service.
"""

from .solver import CAPTCHASolver
from .config import Config
from .extractor import CAPTCHAExtractor
from .preprocessor import ImagePreprocessor
from .ocr import OCRHandler
from .submitter import FormSubmitter

__version__ = "1.0.0"
__author__ = "CAPTCHA Solver Team"
__email__ = "contact@captchasolver.com"

__all__ = [
    "CAPTCHASolver",
    "Config",
    "CAPTCHAExtractor",
    "ImagePreprocessor",
    "OCRHandler",
    "FormSubmitter",
]

# Educational and ethical use disclaimer
DISCLAIMER = """
IMPORTANT: This tool is for educational and research purposes only.
Users must ensure compliance with applicable laws and website terms of service.
The developers are not responsible for any misuse of this software.
"""

print(DISCLAIMER)