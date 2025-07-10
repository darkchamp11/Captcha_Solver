"""Utility functions for CAPTCHA Solver.

This module contains common utility functions used across
the CAPTCHA solver components.
"""

import os
import re
import time
import logging
import hashlib
from typing import Optional, Union, List, Tuple
from pathlib import Path
import numpy as np
from PIL import Image


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file: Optional log file path.
    
    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger("captcha_solver")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def validate_image_path(image_path: Union[str, Path]) -> Path:
    """Validate and convert image path.
    
    Args:
        image_path: Path to image file.
    
    Returns:
        Validated Path object.
    
    Raises:
        FileNotFoundError: If image file doesn't exist.
        ValueError: If file is not a valid image format.
    """
    path = Path(image_path)
    
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {path}")
    
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    
    valid_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
    if path.suffix.lower() not in valid_extensions:
        raise ValueError(f"Invalid image format: {path.suffix}")
    
    return path


def validate_url(url: str) -> bool:
    """Validate URL format.
    
    Args:
        url: URL string to validate.
    
    Returns:
        True if URL is valid, False otherwise.
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'  # domain...
        r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # host...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))


def clean_text(text: str) -> str:
    """Clean and normalize extracted text.
    
    Args:
        text: Raw text from OCR.
    
    Returns:
        Cleaned text string.
    """
    if not text:
        return ""
    
    # Remove non-printable characters
    text = ''.join(char for char in text if char.isprintable())
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove common OCR artifacts
    text = re.sub(r'[|\\/_~`]', '', text)
    
    return text


def calculate_image_hash(image: Union[Image.Image, np.ndarray]) -> str:
    """Calculate hash of image for caching/comparison.
    
    Args:
        image: PIL Image or numpy array.
    
    Returns:
        MD5 hash string of image data.
    """
    if isinstance(image, Image.Image):
        image_bytes = image.tobytes()
    elif isinstance(image, np.ndarray):
        image_bytes = image.tobytes()
    else:
        raise ValueError("Image must be PIL Image or numpy array")
    
    return hashlib.md5(image_bytes).hexdigest()


def ensure_directory(directory: Union[str, Path]) -> Path:
    """Ensure directory exists, create if necessary.
    
    Args:
        directory: Directory path.
    
    Returns:
        Path object of the directory.
    """
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def retry_operation(func, max_attempts: int = 3, delay: float = 1.0, 
                   exceptions: Tuple = (Exception,)):
    """Retry operation with exponential backoff.
    
    Args:
        func: Function to retry.
        max_attempts: Maximum number of attempts.
        delay: Initial delay between attempts.
        exceptions: Tuple of exceptions to catch and retry.
    
    Returns:
        Result of successful function call.
    
    Raises:
        Last exception if all attempts fail.
    """
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            if attempt < max_attempts - 1:
                time.sleep(delay * (2 ** attempt))  # Exponential backoff
            continue
    
    raise last_exception


def get_image_dimensions(image_path: Union[str, Path]) -> Tuple[int, int]:
    """Get image dimensions without loading full image.
    
    Args:
        image_path: Path to image file.
    
    Returns:
        Tuple of (width, height).
    """
    with Image.open(image_path) as img:
        return img.size


def is_image_too_small(image: Union[Image.Image, str, Path], 
                      min_width: int = 50, min_height: int = 20) -> bool:
    """Check if image is too small for OCR processing.
    
    Args:
        image: PIL Image or path to image.
        min_width: Minimum width threshold.
        min_height: Minimum height threshold.
    
    Returns:
        True if image is too small, False otherwise.
    """
    if isinstance(image, (str, Path)):
        width, height = get_image_dimensions(image)
    else:
        width, height = image.size
    
    return width < min_width or height < min_height


def normalize_confidence_score(confidence: float, min_score: float = 0.0, 
                             max_score: float = 100.0) -> float:
    """Normalize confidence score to 0-1 range.
    
    Args:
        confidence: Raw confidence score.
        min_score: Minimum possible score.
        max_score: Maximum possible score.
    
    Returns:
        Normalized confidence score (0-1).
    """
    if max_score == min_score:
        return 1.0
    
    normalized = (confidence - min_score) / (max_score - min_score)
    return max(0.0, min(1.0, normalized))


def format_processing_time(start_time: float) -> str:
    """Format processing time for logging.
    
    Args:
        start_time: Start time from time.time().
    
    Returns:
        Formatted time string.
    """
    elapsed = time.time() - start_time
    
    if elapsed < 1:
        return f"{elapsed*1000:.1f}ms"
    elif elapsed < 60:
        return f"{elapsed:.2f}s"
    else:
        minutes = int(elapsed // 60)
        seconds = elapsed % 60
        return f"{minutes}m {seconds:.1f}s"


def safe_filename(filename: str) -> str:
    """Create safe filename by removing invalid characters.
    
    Args:
        filename: Original filename.
    
    Returns:
        Safe filename string.
    """
    # Remove invalid characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    safe_name = safe_name.strip('. ')
    
    # Ensure not empty
    if not safe_name:
        safe_name = "unnamed"
    
    return safe_name


def get_file_size_mb(file_path: Union[str, Path]) -> float:
    """Get file size in megabytes.
    
    Args:
        file_path: Path to file.
    
    Returns:
        File size in MB.
    """
    size_bytes = Path(file_path).stat().st_size
    return size_bytes / (1024 * 1024)


class Timer:
    """Context manager for timing operations."""
    
    def __init__(self, description: str = "Operation"):
        self.description = description
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
    
    @property
    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0.0
        
        end = self.end_time or time.time()
        return end - self.start_time
    
    def __str__(self) -> str:
        return f"{self.description}: {format_processing_time(self.start_time or time.time())}"