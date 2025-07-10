#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Advanced Configuration Example for CAPTCHA Solver

This example demonstrates how to use advanced configuration options
to customize the CAPTCHA solver for different types of CAPTCHAs.
"""

import os
import yaml
from pathlib import Path
from captcha_solver import CAPTCHASolver, Config

# Example directory for saving processed images
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def example_yaml_config():
    """Example of loading configuration from a YAML file"""
    print("\n=== Loading Configuration from YAML ===\n")
    
    # Create a sample YAML configuration
    config_yaml = """
    tesseract:
      config: "--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
      timeout: 30
      language: "eng"

    preprocessing:
      steps:
        - "grayscale"
        - "denoise"
        - "threshold"
        - "enhance"
      
      grayscale:
        method: "weighted"
      
      denoise:
        method: "gaussian"
        kernel_size: 3
      
      threshold:
        method: "adaptive"
        block_size: 11
        c_value: 2

    ocr:
      confidence_threshold: 70
      character_whitelist: "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
      multiple_configs: true
    """
    
    # Save the YAML configuration to a file
    config_path = Path("captcha_config.yaml")
    with open(config_path, "w") as f:
        f.write(config_yaml)
    
    # Load the configuration from the YAML file
    config = Config.from_yaml(config_path)
    
    # Initialize the solver with the configuration
    solver = CAPTCHASolver(config=config)
    
    print(f"Configuration loaded from {config_path}")
    print(f"Tesseract config: {solver.config.get('tesseract.config')}")
    print(f"Preprocessing steps: {solver.config.get('preprocessing.steps')}")
    print(f"OCR confidence threshold: {solver.config.get('ocr.confidence_threshold')}")
    
    # Clean up the temporary file
    os.remove(config_path)


def example_dict_config():
    """Example of using a Python dictionary for configuration"""
    print("\n=== Using Dictionary Configuration ===\n")
    
    # Create a configuration dictionary
    config_dict = {
        "tesseract": {
            "config": "--psm 7 -c tessedit_char_whitelist=0123456789",
            "timeout": 20
        },
        "preprocessing": {
            "steps": ["grayscale", "threshold", "denoise"],
            "threshold": {
                "method": "otsu"
            },
            "denoise": {
                "method": "median",
                "kernel_size": 5
            }
        },
        "ocr": {
            "confidence_threshold": 50,
            "character_whitelist": "0123456789"
        }
    }
    
    # Initialize the solver with the configuration dictionary
    solver = CAPTCHASolver(config=config_dict)
    
    print("Configuration loaded from dictionary")
    print(f"Tesseract config: {solver.config.get('tesseract.config')}")
    print(f"Preprocessing steps: {solver.config.get('preprocessing.steps')}")
    print(f"OCR confidence threshold: {solver.config.get('ocr.confidence_threshold')}")


def example_numeric_captcha():
    """Example configuration for numeric CAPTCHAs"""
    print("\n=== Numeric CAPTCHA Configuration ===\n")
    
    # Configuration optimized for numeric CAPTCHAs
    config = {
        "tesseract": {
            "config": "--psm 8 -c tessedit_char_whitelist=0123456789"
        },
        "preprocessing": {
            "steps": ["grayscale", "threshold", "denoise", "dilate"],
            "threshold": {
                "method": "binary",
                "threshold": 180
            }
        },
        "ocr": {
            "confidence_threshold": 60,
            "character_whitelist": "0123456789"
        }
    }
    
    solver = CAPTCHASolver(config=config)
    print("Numeric CAPTCHA configuration loaded")
    print(f"Character whitelist: {solver.config.get('ocr.character_whitelist')}")


def example_alphanumeric_captcha():
    """Example configuration for alphanumeric CAPTCHAs"""
    print("\n=== Alphanumeric CAPTCHA Configuration ===\n")
    
    # Configuration optimized for alphanumeric CAPTCHAs
    config = {
        "tesseract": {
            "config": "--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
        },
        "preprocessing": {
            "steps": ["grayscale", "denoise", "threshold", "enhance", "dilate"],
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
            "confidence_threshold": 40,
            "multiple_configs": True
        }
    }
    
    solver = CAPTCHASolver(config=config)
    print("Alphanumeric CAPTCHA configuration loaded")
    print(f"Tesseract config: {solver.config.get('tesseract.config')}")


def example_runtime_config_update():
    """Example of updating configuration at runtime"""
    print("\n=== Runtime Configuration Updates ===\n")
    
    # Start with a basic configuration
    solver = CAPTCHASolver()
    
    print("Initial configuration:")
    print(f"Preprocessing steps: {solver.config.get('preprocessing.steps')}")
    print(f"OCR confidence threshold: {solver.config.get('ocr.confidence_threshold')}")
    
    # Update configuration at runtime
    solver.config.set("preprocessing.steps", ["grayscale", "threshold", "dilate"])
    solver.config.set("ocr.confidence_threshold", 75)
    solver.config.set("tesseract.config", "--psm 10 --oem 3")
    
    print("\nUpdated configuration:")
    print(f"Preprocessing steps: {solver.config.get('preprocessing.steps')}")
    print(f"OCR confidence threshold: {solver.config.get('ocr.confidence_threshold')}")
    print(f"Tesseract config: {solver.config.get('tesseract.config')}")


def example_save_config():
    """Example of saving configuration to a file"""
    print("\n=== Saving Configuration ===\n")
    
    # Create a solver with custom configuration
    config = {
        "tesseract": {
            "config": "--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        },
        "preprocessing": {
            "steps": ["grayscale", "threshold", "denoise", "enhance"]
        },
        "ocr": {
            "confidence_threshold": 65
        }
    }
    
    solver = CAPTCHASolver(config=config)
    
    # Save the configuration to a YAML file
    config_path = Path("saved_config.yaml")
    solver.config.save(config_path)
    
    print(f"Configuration saved to {config_path}")
    
    # Load the saved configuration
    new_solver = CAPTCHASolver(config=Config.from_yaml(config_path))
    
    print("Configuration loaded from saved file:")
    print(f"Tesseract config: {new_solver.config.get('tesseract.config')}")
    print(f"Preprocessing steps: {new_solver.config.get('preprocessing.steps')}")
    
    # Clean up the temporary file
    os.remove(config_path)


if __name__ == "__main__":
    print("CAPTCHA Solver - Advanced Configuration Examples")
    print("=" * 50)
    
    # Run the examples
    example_yaml_config()
    example_dict_config()
    example_numeric_captcha()
    example_alphanumeric_captcha()
    example_runtime_config_update()
    example_save_config()
    
    print("\n=== Examples Completed ===\n")