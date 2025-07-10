"""Configuration management for CAPTCHA Solver.

This module handles loading and validating configuration settings
for all components of the CAPTCHA solver system.
"""

import json
import os
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for CAPTCHA solver components."""
    
    DEFAULT_CONFIG = {
        "tesseract": {
            "cmd": "/usr/bin/tesseract",
            "config": "--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        },
        "preprocessing": {
            "steps": ["grayscale", "denoise", "threshold", "morphology"],
            "gaussian_blur": {"kernel_size": [5, 5], "sigma": 0},
            "threshold": {"type": "adaptive", "max_value": 255, "block_size": 11, "c": 2},
            "morphology": {"kernel_size": [3, 3], "iterations": 1}
        },
        "selenium": {
            "driver": "chrome",
            "headless": True,
            "timeout": 10,
            "window_size": [1920, 1080]
        },
        "ocr": {
            "confidence_threshold": 60,
            "dpi": 300,
            "language": "eng"
        },
        "extraction": {
            "timeout": 30,
            "retry_attempts": 3,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration manager.
        
        Args:
            config_file: Path to JSON configuration file. If None, uses defaults.
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_file and os.path.exists(config_file):
            self._load_from_file(config_file)
        
        self.validate_config()
    
    def _load_from_file(self, config_file: str) -> None:
        """Load configuration from JSON file.
        
        Args:
            config_file: Path to configuration file.
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
            
            # Deep merge with default config
            self._deep_merge(self.config, file_config)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ValueError(f"Error loading config file {config_file}: {e}")
    
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]) -> None:
        """Deep merge two dictionaries.
        
        Args:
            base: Base dictionary to merge into.
            update: Dictionary with updates to merge.
        """
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def get_tesseract_config(self) -> Dict[str, Any]:
        """Get Tesseract OCR configuration.
        
        Returns:
            Dictionary with Tesseract settings.
        """
        return self.config["tesseract"]
    
    def get_preprocessing_config(self) -> Dict[str, Any]:
        """Get image preprocessing configuration.
        
        Returns:
            Dictionary with preprocessing settings.
        """
        return self.config["preprocessing"]
    
    def get_selenium_config(self) -> Dict[str, Any]:
        """Get Selenium WebDriver configuration.
        
        Returns:
            Dictionary with Selenium settings.
        """
        return self.config["selenium"]
    
    def get_ocr_config(self) -> Dict[str, Any]:
        """Get OCR configuration.
        
        Returns:
            Dictionary with OCR settings.
        """
        return self.config["ocr"]
    
    def get_extraction_config(self) -> Dict[str, Any]:
        """Get extraction configuration.
        
        Returns:
            Dictionary with extraction settings.
        """
        return self.config["extraction"]
    
    def validate_config(self) -> None:
        """Validate configuration parameters.
        
        Raises:
            ValueError: If configuration is invalid.
        """
        required_sections = ["tesseract", "preprocessing", "selenium", "ocr", "extraction"]
        
        for section in required_sections:
            if section not in self.config:
                raise ValueError(f"Missing required configuration section: {section}")
        
        # Validate specific parameters
        selenium_config = self.get_selenium_config()
        if selenium_config["timeout"] <= 0:
            raise ValueError("Selenium timeout must be positive")
        
        ocr_config = self.get_ocr_config()
        if not 0 <= ocr_config["confidence_threshold"] <= 100:
            raise ValueError("OCR confidence threshold must be between 0 and 100")
        
        preprocessing_config = self.get_preprocessing_config()
        valid_steps = ["grayscale", "denoise", "threshold", "morphology", "skew_correction"]
        for step in preprocessing_config["steps"]:
            if step not in valid_steps:
                raise ValueError(f"Invalid preprocessing step: {step}")
    
    def save_to_file(self, config_file: str) -> None:
        """Save current configuration to file.
        
        Args:
            config_file: Path to save configuration file.
        """
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise ValueError(f"Error saving config file {config_file}: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation).
            default: Default value if key not found.
        
        Returns:
            Configuration value or default.
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key.
        
        Args:
            key: Configuration key (supports dot notation).
            value: Value to set.
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value