#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for the Config class.
"""

import os
import unittest
from pathlib import Path
import tempfile
import yaml

# Add parent directory to path to import captcha_solver
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from captcha_solver.config import Config


class TestConfig(unittest.TestCase):
    """Test cases for the Config class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up temporary directory
        self.temp_dir.cleanup()
    
    def test_initialization_empty(self):
        """Test initialization with empty configuration."""
        config = Config()
        
        # Verify that default values are set
        self.assertIsNotNone(config.get("ocr.engine"))
        self.assertIsNotNone(config.get("preprocessing.steps"))
        self.assertIsNotNone(config.get("extraction.selectors.captcha_img"))
        self.assertIsNotNone(config.get("submission.selectors.captcha_input"))
    
    def test_initialization_with_dict(self):
        """Test initialization with a dictionary."""
        config_dict = {
            "ocr": {
                "engine": "custom",
                "custom": {
                    "module": "my_ocr_module",
                    "function": "recognize_text"
                }
            },
            "preprocessing": {
                "steps": ["grayscale", "threshold", "denoise"]
            }
        }
        
        config = Config(config_dict)
        
        # Verify that the values from the dictionary are set
        self.assertEqual(config.get("ocr.engine"), "custom")
        self.assertEqual(config.get("ocr.custom.module"), "my_ocr_module")
        self.assertEqual(config.get("ocr.custom.function"), "recognize_text")
        self.assertEqual(config.get("preprocessing.steps"), ["grayscale", "threshold", "denoise"])
        
        # Verify that default values are set for keys not in the dictionary
        self.assertIsNotNone(config.get("extraction.selectors.captcha_img"))
        self.assertIsNotNone(config.get("submission.selectors.captcha_input"))
    
    def test_initialization_with_yaml_file(self):
        """Test initialization with a YAML file."""
        # Create a test YAML file
        yaml_content = """
        ocr:
          engine: tesseract
          tesseract:
            path: /usr/bin/tesseract
            config: --psm 8 --oem 3
            lang: eng
        preprocessing:
          steps:
            - grayscale
            - threshold
            - denoise
          grayscale:
            method: weighted
          threshold:
            method: binary
            threshold: 150
          denoise:
            method: gaussian
            kernel_size: 3
        """
        
        yaml_file = self.temp_path / "test_config.yaml"
        with open(yaml_file, "w") as f:
            f.write(yaml_content)
        
        config = Config(yaml_file)
        
        # Verify that the values from the YAML file are set
        self.assertEqual(config.get("ocr.engine"), "tesseract")
        self.assertEqual(config.get("ocr.tesseract.path"), "/usr/bin/tesseract")
        self.assertEqual(config.get("ocr.tesseract.config"), "--psm 8 --oem 3")
        self.assertEqual(config.get("ocr.tesseract.lang"), "eng")
        self.assertEqual(config.get("preprocessing.steps"), ["grayscale", "threshold", "denoise"])
        self.assertEqual(config.get("preprocessing.grayscale.method"), "weighted")
        self.assertEqual(config.get("preprocessing.threshold.method"), "binary")
        self.assertEqual(config.get("preprocessing.threshold.threshold"), 150)
        self.assertEqual(config.get("preprocessing.denoise.method"), "gaussian")
        self.assertEqual(config.get("preprocessing.denoise.kernel_size"), 3)
    
    def test_get_existing_key(self):
        """Test getting an existing key."""
        config = Config({
            "ocr": {
                "engine": "tesseract",
                "tesseract": {
                    "path": "/usr/bin/tesseract"
                }
            }
        })
        
        # Verify that get returns the correct value for existing keys
        self.assertEqual(config.get("ocr.engine"), "tesseract")
        self.assertEqual(config.get("ocr.tesseract.path"), "/usr/bin/tesseract")
    
    def test_get_nonexistent_key(self):
        """Test getting a nonexistent key."""
        config = Config()
        
        # Verify that get returns None for nonexistent keys
        self.assertIsNone(config.get("nonexistent.key"))
        
        # Verify that get returns the default value for nonexistent keys
        self.assertEqual(config.get("nonexistent.key", "default"), "default")
    
    def test_set_new_key(self):
        """Test setting a new key."""
        config = Config()
        
        # Set a new key
        config.set("new.key", "value")
        
        # Verify that the key was set
        self.assertEqual(config.get("new.key"), "value")
    
    def test_set_existing_key(self):
        """Test setting an existing key."""
        config = Config({
            "ocr": {
                "engine": "tesseract"
            }
        })
        
        # Set an existing key
        config.set("ocr.engine", "custom")
        
        # Verify that the key was updated
        self.assertEqual(config.get("ocr.engine"), "custom")
    
    def test_set_nested_key(self):
        """Test setting a nested key."""
        config = Config()
        
        # Set a nested key
        config.set("nested.key.path", "value")
        
        # Verify that the key was set and the nested structure was created
        self.assertEqual(config.get("nested.key.path"), "value")
        self.assertIsInstance(config.config["nested"], dict)
        self.assertIsInstance(config.config["nested"]["key"], dict)
        self.assertEqual(config.config["nested"]["key"]["path"], "value")
    
    def test_update_with_dict(self):
        """Test updating with a dictionary."""
        config = Config({
            "ocr": {
                "engine": "tesseract",
                "tesseract": {
                    "path": "/usr/bin/tesseract"
                }
            }
        })
        
        # Update with a dictionary
        config.update({
            "ocr": {
                "engine": "custom",
                "custom": {
                    "module": "my_ocr_module"
                }
            },
            "preprocessing": {
                "steps": ["grayscale"]
            }
        })
        
        # Verify that the values were updated
        self.assertEqual(config.get("ocr.engine"), "custom")
        self.assertEqual(config.get("ocr.custom.module"), "my_ocr_module")
        self.assertEqual(config.get("preprocessing.steps"), ["grayscale"])
        
        # Verify that values not in the update dictionary were preserved
        self.assertEqual(config.get("ocr.tesseract.path"), "/usr/bin/tesseract")
    
    def test_update_with_yaml_file(self):
        """Test updating with a YAML file."""
        config = Config({
            "ocr": {
                "engine": "tesseract",
                "tesseract": {
                    "path": "/usr/bin/tesseract"
                }
            }
        })
        
        # Create a test YAML file
        yaml_content = """
        ocr:
          engine: custom
          custom:
            module: my_ocr_module
        preprocessing:
          steps:
            - grayscale
        """
        
        yaml_file = self.temp_path / "update_config.yaml"
        with open(yaml_file, "w") as f:
            f.write(yaml_content)
        
        # Update with the YAML file
        config.update(yaml_file)
        
        # Verify that the values were updated
        self.assertEqual(config.get("ocr.engine"), "custom")
        self.assertEqual(config.get("ocr.custom.module"), "my_ocr_module")
        self.assertEqual(config.get("preprocessing.steps"), ["grayscale"])
        
        # Verify that values not in the update YAML were preserved
        self.assertEqual(config.get("ocr.tesseract.path"), "/usr/bin/tesseract")
    
    def test_save_to_yaml(self):
        """Test saving to a YAML file."""
        config = Config({
            "ocr": {
                "engine": "tesseract",
                "tesseract": {
                    "path": "/usr/bin/tesseract",
                    "config": "--psm 8 --oem 3",
                    "lang": "eng"
                }
            },
            "preprocessing": {
                "steps": ["grayscale", "threshold", "denoise"],
                "grayscale": {
                    "method": "weighted"
                },
                "threshold": {
                    "method": "binary",
                    "threshold": 150
                },
                "denoise": {
                    "method": "gaussian",
                    "kernel_size": 3
                }
            }
        })
        
        # Save to a YAML file
        yaml_file = self.temp_path / "saved_config.yaml"
        config.save(yaml_file)
        
        # Verify that the file was created
        self.assertTrue(yaml_file.exists())
        
        # Load the saved file and verify the content
        with open(yaml_file, "r") as f:
            loaded_config = yaml.safe_load(f)
        
        self.assertEqual(loaded_config["ocr"]["engine"], "tesseract")
        self.assertEqual(loaded_config["ocr"]["tesseract"]["path"], "/usr/bin/tesseract")
        self.assertEqual(loaded_config["ocr"]["tesseract"]["config"], "--psm 8 --oem 3")
        self.assertEqual(loaded_config["ocr"]["tesseract"]["lang"], "eng")
        self.assertEqual(loaded_config["preprocessing"]["steps"], ["grayscale", "threshold", "denoise"])
        self.assertEqual(loaded_config["preprocessing"]["grayscale"]["method"], "weighted")
        self.assertEqual(loaded_config["preprocessing"]["threshold"]["method"], "binary")
        self.assertEqual(loaded_config["preprocessing"]["threshold"]["threshold"], 150)
        self.assertEqual(loaded_config["preprocessing"]["denoise"]["method"], "gaussian")
        self.assertEqual(loaded_config["preprocessing"]["denoise"]["kernel_size"], 3)
    
    def test_validate_config(self):
        """Test validating a configuration."""
        # Valid configuration
        valid_config = Config({
            "ocr": {
                "engine": "tesseract",
                "tesseract": {
                    "path": "/usr/bin/tesseract"
                }
            },
            "preprocessing": {
                "steps": ["grayscale", "threshold"]
            }
        })
        
        # Verify that validate returns True for a valid configuration
        self.assertTrue(valid_config.validate())
        
        # Invalid configuration (missing required key)
        invalid_config = Config({})
        invalid_config.config = {}  # Clear default values
        
        # Verify that validate returns False for an invalid configuration
        self.assertFalse(invalid_config.validate())
    
    def test_get_default_config(self):
        """Test getting the default configuration."""
        default_config = Config.get_default_config()
        
        # Verify that the default configuration has the expected keys
        self.assertIn("ocr", default_config)
        self.assertIn("preprocessing", default_config)
        self.assertIn("extraction", default_config)
        self.assertIn("submission", default_config)
        
        # Verify that the default configuration has the expected values
        self.assertEqual(default_config["ocr"]["engine"], "tesseract")
        self.assertIsInstance(default_config["preprocessing"]["steps"], list)
        self.assertIsInstance(default_config["extraction"]["selectors"], dict)
        self.assertIsInstance(default_config["submission"]["selectors"], dict)
    
    def test_merge_configs(self):
        """Test merging configurations."""
        config1 = {
            "ocr": {
                "engine": "tesseract",
                "tesseract": {
                    "path": "/usr/bin/tesseract"
                }
            }
        }
        
        config2 = {
            "ocr": {
                "engine": "custom",
                "custom": {
                    "module": "my_ocr_module"
                }
            },
            "preprocessing": {
                "steps": ["grayscale"]
            }
        }
        
        # Merge the configurations
        merged_config = Config._merge_configs(config1, config2)
        
        # Verify that the merged configuration has the expected values
        self.assertEqual(merged_config["ocr"]["engine"], "custom")
        self.assertEqual(merged_config["ocr"]["tesseract"]["path"], "/usr/bin/tesseract")
        self.assertEqual(merged_config["ocr"]["custom"]["module"], "my_ocr_module")
        self.assertEqual(merged_config["preprocessing"]["steps"], ["grayscale"])
    
    def test_to_dict(self):
        """Test converting to a dictionary."""
        config_dict = {
            "ocr": {
                "engine": "tesseract",
                "tesseract": {
                    "path": "/usr/bin/tesseract",
                    "config": "--psm 8 --oem 3",
                    "lang": "eng"
                }
            },
            "preprocessing": {
                "steps": ["grayscale", "threshold", "denoise"],
                "grayscale": {
                    "method": "weighted"
                },
                "threshold": {
                    "method": "binary",
                    "threshold": 150
                },
                "denoise": {
                    "method": "gaussian",
                    "kernel_size": 3
                }
            }
        }
        
        config = Config(config_dict)
        
        # Convert to a dictionary
        result_dict = config.to_dict()
        
        # Verify that the result is a dictionary with the expected values
        self.assertIsInstance(result_dict, dict)
        self.assertEqual(result_dict["ocr"]["engine"], "tesseract")
        self.assertEqual(result_dict["ocr"]["tesseract"]["path"], "/usr/bin/tesseract")
        self.assertEqual(result_dict["ocr"]["tesseract"]["config"], "--psm 8 --oem 3")
        self.assertEqual(result_dict["ocr"]["tesseract"]["lang"], "eng")
        self.assertEqual(result_dict["preprocessing"]["steps"], ["grayscale", "threshold", "denoise"])
        self.assertEqual(result_dict["preprocessing"]["grayscale"]["method"], "weighted")
        self.assertEqual(result_dict["preprocessing"]["threshold"]["method"], "binary")
        self.assertEqual(result_dict["preprocessing"]["threshold"]["threshold"], 150)
        self.assertEqual(result_dict["preprocessing"]["denoise"]["method"], "gaussian")
        self.assertEqual(result_dict["preprocessing"]["denoise"]["kernel_size"], 3)


if __name__ == "__main__":
    unittest.main()