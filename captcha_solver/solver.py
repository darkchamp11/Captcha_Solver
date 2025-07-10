"""Main CAPTCHA solver class.

This module contains the main CAPTCHASolver class that orchestrates
all components to provide a complete CAPTCHA solving solution.
"""

from PIL import Image
from typing import Optional, Dict, Any, Union, List
import logging
import os
from pathlib import Path
import time

from .config import Config
from .extractor import CAPTCHAExtractor
from .preprocessor import ImagePreprocessor
from .ocr import OCRHandler
from .submitter import FormSubmitter
from .utils import (
    setup_logging, validate_image_path, Timer, 
    calculate_image_hash, ensure_directory
)


class CAPTCHASolver:
    """Main CAPTCHA solver class that coordinates all components."""
    
    def __init__(self, config: Optional[Union[str, dict, Config]] = None, 
                 log_level: str = "INFO", log_file: Optional[str] = None):
        """Initialize CAPTCHA solver with configuration.
        
        Args:
            config: Configuration (file path, dict, or Config object).
            log_level: Logging level.
            log_file: Optional log file path.
        """
        # Set up logging
        self.logger = setup_logging(log_level, log_file)
        self.logger.info("Initializing CAPTCHA Solver")
        
        # Load configuration
        if isinstance(config, Config):
            self.config = config
        elif isinstance(config, dict):
            self.config = Config()
            self.config.config.update(config)
        elif isinstance(config, str):
            self.config = Config(config)
        else:
            self.config = Config()
        
        # Initialize components
        self.extractor = CAPTCHAExtractor(self.config.config)
        self.preprocessor = ImagePreprocessor(self.config.get_preprocessing_config())
        self.ocr_handler = OCRHandler(self.config.config)
        
        # State variables
        self.last_processed_image = None
        self.last_confidence = 0.0
        self.last_result = ""
        self.processing_history = []
        
        # Cache directory for debugging
        self.cache_dir = ensure_directory("captcha_cache")
        
        self.logger.info("CAPTCHA Solver initialized successfully")
    
    def solve_from_file(self, image_path: Union[str, Path], 
                       save_processed: bool = False) -> str:
        """Solve CAPTCHA from image file.
        
        Args:
            image_path: Path to CAPTCHA image file.
            save_processed: Whether to save processed image for debugging.
        
        Returns:
            Solved CAPTCHA text string.
        """
        try:
            with Timer(f"Solving CAPTCHA from file: {image_path}") as timer:
                # Validate image path
                validated_path = validate_image_path(image_path)
                
                # Load image
                image = Image.open(validated_path)
                self.logger.info(f"Loaded image: {validated_path} ({image.size[0]}x{image.size[1]})")
                
                # Solve CAPTCHA
                result = self._solve_image(image, str(validated_path), save_processed)
                
                self.logger.info(f"CAPTCHA solved in {timer.elapsed:.3f}s: '{result}'")
                return result
                
        except Exception as e:
            self.logger.error(f"Failed to solve CAPTCHA from file {image_path}: {e}")
            return ""
    
    def solve_from_url(self, url: str, captcha_selectors: Optional[List[str]] = None,
                      save_processed: bool = False) -> str:
        """Extract and solve CAPTCHA from web page.
        
        Args:
            url: URL of web page containing CAPTCHA.
            captcha_selectors: CSS selectors for CAPTCHA elements.
            save_processed: Whether to save processed image for debugging.
        
        Returns:
            Solved CAPTCHA text string.
        """
        try:
            with Timer(f"Solving CAPTCHA from URL: {url}") as timer:
                # Extract CAPTCHA image
                image = self.extractor.extract_from_url(url, captcha_selectors)
                
                if not image:
                    self.logger.error(f"Failed to extract CAPTCHA from URL: {url}")
                    return ""
                
                self.logger.info(f"Extracted CAPTCHA image: {image.size[0]}x{image.size[1]}")
                
                # Solve CAPTCHA
                result = self._solve_image(image, url, save_processed)
                
                self.logger.info(f"CAPTCHA solved in {timer.elapsed:.3f}s: '{result}'")
                return result
                
        except Exception as e:
            self.logger.error(f"Failed to solve CAPTCHA from URL {url}: {e}")
            return ""
    
    def solve_from_element(self, web_element, driver=None, 
                          save_processed: bool = False) -> str:
        """Solve CAPTCHA from Selenium WebElement.
        
        Args:
            web_element: Selenium WebElement containing CAPTCHA.
            driver: Selenium WebDriver instance.
            save_processed: Whether to save processed image for debugging.
        
        Returns:
            Solved CAPTCHA text string.
        """
        try:
            with Timer("Solving CAPTCHA from WebElement") as timer:
                # Extract CAPTCHA image
                image = self.extractor.extract_from_element(web_element, driver)
                
                if not image:
                    self.logger.error("Failed to extract CAPTCHA from WebElement")
                    return ""
                
                self.logger.info(f"Extracted CAPTCHA image: {image.size[0]}x{image.size[1]}")
                
                # Solve CAPTCHA
                source = driver.current_url if driver else "WebElement"
                result = self._solve_image(image, source, save_processed)
                
                self.logger.info(f"CAPTCHA solved in {timer.elapsed:.3f}s: '{result}'")
                return result
                
        except Exception as e:
            self.logger.error(f"Failed to solve CAPTCHA from WebElement: {e}")
            return ""
    
    def _solve_image(self, image: Image.Image, source: str, 
                    save_processed: bool = False) -> str:
        """Internal method to solve CAPTCHA from PIL Image.
        
        Args:
            image: PIL Image object.
            source: Source description for logging.
            save_processed: Whether to save processed image.
        
        Returns:
            Solved CAPTCHA text string.
        """
        try:
            # Calculate image hash for caching/tracking
            image_hash = calculate_image_hash(image)
            
            # Save original image if debugging
            if save_processed:
                original_path = self.cache_dir / f"original_{image_hash}.png"
                image.save(original_path)
                self.logger.debug(f"Saved original image: {original_path}")
            
            # Preprocess image
            with Timer("Image preprocessing") as preprocess_timer:
                processed_image = self.preprocessor.preprocess(image)
                self.last_processed_image = processed_image
            
            self.logger.debug(f"Image preprocessed in {preprocess_timer.elapsed:.3f}s")
            
            # Save processed image if debugging
            if save_processed:
                processed_path = self.cache_dir / f"processed_{image_hash}.png"
                processed_image.save(processed_path)
                self.logger.debug(f"Saved processed image: {processed_path}")
            
            # Perform OCR
            with Timer("OCR recognition") as ocr_timer:
                # Try multiple OCR configurations for better results
                result, confidence = self.ocr_handler.recognize_with_multiple_configs(processed_image)
                
                self.last_result = result
                self.last_confidence = confidence
            
            self.logger.debug(f"OCR completed in {ocr_timer.elapsed:.3f}s")
            
            # Record processing history
            self._record_processing(source, image_hash, result, confidence)
            
            # Validate result
            if not self._validate_result(result, confidence):
                self.logger.warning(f"Low confidence result: '{result}' ({confidence:.1f}%)")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to solve CAPTCHA image: {e}")
            return ""
    
    def _validate_result(self, result: str, confidence: float) -> bool:
        """Validate OCR result quality.
        
        Args:
            result: OCR result text.
            confidence: OCR confidence score.
        
        Returns:
            True if result appears valid, False otherwise.
        """
        # Check minimum confidence threshold
        min_confidence = self.config.get("ocr.confidence_threshold", 60)
        if confidence < min_confidence:
            return False
        
        # Check result is not empty
        if not result or not result.strip():
            return False
        
        # Check reasonable length (most CAPTCHAs are 3-8 characters)
        if len(result) < 3 or len(result) > 10:
            self.logger.warning(f"Unusual CAPTCHA length: {len(result)} characters")
        
        return True
    
    def _record_processing(self, source: str, image_hash: str, 
                          result: str, confidence: float) -> None:
        """Record processing attempt in history.
        
        Args:
            source: Source of the CAPTCHA.
            image_hash: Hash of the processed image.
            result: OCR result.
            confidence: OCR confidence.
        """
        record = {
            "timestamp": time.time(),
            "source": source,
            "image_hash": image_hash,
            "result": result,
            "confidence": confidence,
            "preprocessing_steps": self.preprocessor.processing_steps
        }
        
        self.processing_history.append(record)
        
        # Keep only last 100 records
        if len(self.processing_history) > 100:
            self.processing_history = self.processing_history[-100:]
    
    def get_processed_image(self) -> Optional[Image.Image]:
        """Return the last processed image for debugging.
        
        Returns:
            PIL Image object or None if no image processed yet.
        """
        return self.last_processed_image
    
    def get_confidence(self) -> float:
        """Return OCR confidence score from last recognition.
        
        Returns:
            Confidence score (0-100).
        """
        return self.last_confidence
    
    def get_last_result(self) -> str:
        """Return last OCR result.
        
        Returns:
            Last OCR result string.
        """
        return self.last_result
    
    def solve_batch(self, image_paths: List[Union[str, Path]], 
                   save_processed: bool = False) -> List[Dict[str, Any]]:
        """Solve multiple CAPTCHA images in batch.
        
        Args:
            image_paths: List of image file paths.
            save_processed: Whether to save processed images.
        
        Returns:
            List of dictionaries with results for each image.
        """
        results = []
        
        with Timer(f"Batch processing {len(image_paths)} images") as timer:
            for i, image_path in enumerate(image_paths):
                self.logger.info(f"Processing image {i+1}/{len(image_paths)}: {image_path}")
                
                try:
                    result = self.solve_from_file(image_path, save_processed)
                    
                    results.append({
                        "path": str(image_path),
                        "result": result,
                        "confidence": self.last_confidence,
                        "success": bool(result.strip()),
                        "processing_time": timer.elapsed
                    })
                    
                except Exception as e:
                    self.logger.error(f"Failed to process {image_path}: {e}")
                    results.append({
                        "path": str(image_path),
                        "result": "",
                        "confidence": 0.0,
                        "success": False,
                        "error": str(e),
                        "processing_time": timer.elapsed
                    })
        
        # Calculate batch statistics
        successful = sum(1 for r in results if r["success"])
        avg_confidence = sum(r["confidence"] for r in results if r["success"]) / max(successful, 1)
        
        self.logger.info(f"Batch completed: {successful}/{len(image_paths)} successful, "
                        f"avg confidence: {avg_confidence:.1f}%, time: {timer.elapsed:.3f}s")
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics.
        
        Returns:
            Dictionary with processing statistics.
        """
        if not self.processing_history:
            return {"message": "No processing history available"}
        
        successful = [r for r in self.processing_history if r["result"].strip()]
        
        return {
            "total_processed": len(self.processing_history),
            "successful": len(successful),
            "success_rate": len(successful) / len(self.processing_history) * 100,
            "average_confidence": sum(r["confidence"] for r in successful) / max(len(successful), 1),
            "last_24h": len([r for r in self.processing_history 
                           if time.time() - r["timestamp"] < 86400]),
            "common_sources": self._get_common_sources(),
            "preprocessing_config": self.preprocessor.get_processing_info()
        }
    
    def _get_common_sources(self) -> Dict[str, int]:
        """Get most common CAPTCHA sources.
        
        Returns:
            Dictionary mapping sources to count.
        """
        sources = {}
        for record in self.processing_history:
            source = record["source"]
            sources[source] = sources.get(source, 0) + 1
        
        # Return top 10 sources
        return dict(sorted(sources.items(), key=lambda x: x[1], reverse=True)[:10])
    
    def configure_preprocessing(self, steps: List[str]) -> None:
        """Configure preprocessing steps.
        
        Args:
            steps: List of preprocessing step names.
        """
        self.preprocessor.processing_steps = steps
        self.logger.info(f"Updated preprocessing steps: {steps}")
    
    def configure_ocr(self, config: str) -> None:
        """Configure OCR settings.
        
        Args:
            config: Tesseract configuration string.
        """
        self.ocr_handler.configure_tesseract(config)
        self.logger.info(f"Updated OCR configuration: {config}")
    
    def test_components(self) -> Dict[str, bool]:
        """Test all components for proper functionality.
        
        Returns:
            Dictionary with component test results.
        """
        results = {}
        
        # Test OCR
        try:
            results["ocr"] = self.ocr_handler.is_tesseract_available()
        except Exception as e:
            self.logger.error(f"OCR test failed: {e}")
            results["ocr"] = False
        
        # Test preprocessing
        try:
            # Create a simple test image
            test_image = Image.new('RGB', (100, 50), color='white')
            processed = self.preprocessor.preprocess(test_image)
            results["preprocessing"] = isinstance(processed, Image.Image)
        except Exception as e:
            self.logger.error(f"Preprocessing test failed: {e}")
            results["preprocessing"] = False
        
        # Test extraction
        try:
            info = self.extractor.get_extraction_info()
            results["extraction"] = "supported_methods" in info
        except Exception as e:
            self.logger.error(f"Extraction test failed: {e}")
            results["extraction"] = False
        
        # Test configuration
        try:
            self.config.validate_config()
            results["config"] = True
        except Exception as e:
            self.logger.error(f"Config test failed: {e}")
            results["config"] = False
        
        return results
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information.
        
        Returns:
            Dictionary with system information.
        """
        return {
            "version": "1.0.0",
            "components": {
                "extractor": self.extractor.get_extraction_info(),
                "preprocessor": self.preprocessor.get_processing_info(),
                "ocr": self.ocr_handler.get_ocr_info(),
                "config": self.config.config
            },
            "component_tests": self.test_components(),
            "statistics": self.get_statistics(),
            "cache_directory": str(self.cache_dir)
        }
    
    def cleanup(self) -> None:
        """Clean up resources."""
        try:
            self.extractor.close()
            self.logger.info("CAPTCHA Solver cleanup completed")
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()