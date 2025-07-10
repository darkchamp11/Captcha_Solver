"""Image preprocessing module for CAPTCHA Solver.

This module handles all image preprocessing operations to enhance
CAPTCHA images for better OCR recognition accuracy.
"""

import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance
from typing import Union, List, Tuple, Optional
import logging
from .utils import Timer


class ImagePreprocessor:
    """Image preprocessing pipeline for CAPTCHA images."""
    
    def __init__(self, config: dict):
        """Initialize preprocessor with configuration.
        
        Args:
            config: Preprocessing configuration dictionary.
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.processing_steps = config.get("steps", ["grayscale", "denoise", "threshold"])
    
    def preprocess(self, image: Union[Image.Image, np.ndarray]) -> Image.Image:
        """Apply full preprocessing pipeline to image.
        
        Args:
            image: Input image (PIL Image or numpy array).
        
        Returns:
            Preprocessed PIL Image.
        """
        with Timer("Image preprocessing") as timer:
            # Convert to PIL Image if numpy array
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)
            
            # Apply preprocessing steps in order
            for step in self.processing_steps:
                if step == "grayscale":
                    image = self.convert_to_grayscale(image)
                elif step == "denoise":
                    image = self.denoise(image)
                elif step == "threshold":
                    image = self.apply_threshold(image)
                elif step == "morphology":
                    image = self.morphological_operations(image)
                elif step == "skew_correction":
                    image = self.correct_skew(image)
                elif step == "enhance":
                    image = self.enhance_image(image)
                else:
                    self.logger.warning(f"Unknown preprocessing step: {step}")
            
            self.logger.debug(f"Preprocessing completed in {timer.elapsed:.3f}s")
            return image
    
    def convert_to_grayscale(self, image: Image.Image) -> Image.Image:
        """Convert image to grayscale.
        
        Args:
            image: Input PIL Image.
        
        Returns:
            Grayscale PIL Image.
        """
        if image.mode != 'L':
            image = image.convert('L')
        return image
    
    def denoise(self, image: Image.Image) -> Image.Image:
        """Remove noise using Gaussian blur and median filter.
        
        Args:
            image: Input PIL Image.
        
        Returns:
            Denoised PIL Image.
        """
        # Convert to numpy for OpenCV operations
        img_array = np.array(image)
        
        # Apply Gaussian blur
        blur_config = self.config.get("gaussian_blur", {"kernel_size": [5, 5], "sigma": 0})
        kernel_size = tuple(blur_config["kernel_size"])
        sigma = blur_config["sigma"]
        
        if sigma == 0:
            sigma = 0.3 * ((kernel_size[0] - 1) * 0.5 - 1) + 0.8
        
        blurred = cv2.GaussianBlur(img_array, kernel_size, sigma)
        
        # Apply median filter
        median_filtered = cv2.medianBlur(blurred, 3)
        
        return Image.fromarray(median_filtered)
    
    def apply_threshold(self, image: Image.Image) -> Image.Image:
        """Apply adaptive thresholding for binarization.
        
        Args:
            image: Input PIL Image.
        
        Returns:
            Thresholded PIL Image.
        """
        img_array = np.array(image)
        
        threshold_config = self.config.get("threshold", {
            "type": "adaptive",
            "max_value": 255,
            "block_size": 11,
            "c": 2
        })
        
        if threshold_config["type"] == "adaptive":
            # Adaptive threshold
            thresholded = cv2.adaptiveThreshold(
                img_array,
                threshold_config["max_value"],
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                threshold_config["block_size"],
                threshold_config["c"]
            )
        else:
            # Simple threshold
            _, thresholded = cv2.threshold(
                img_array,
                0,
                threshold_config["max_value"],
                cv2.THRESH_BINARY + cv2.THRESH_OTSU
            )
        
        return Image.fromarray(thresholded)
    
    def morphological_operations(self, image: Image.Image) -> Image.Image:
        """Apply erosion and dilation operations.
        
        Args:
            image: Input PIL Image.
        
        Returns:
            Processed PIL Image.
        """
        img_array = np.array(image)
        
        morph_config = self.config.get("morphology", {
            "kernel_size": [3, 3],
            "iterations": 1
        })
        
        kernel_size = tuple(morph_config["kernel_size"])
        iterations = morph_config["iterations"]
        
        # Create morphological kernel
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
        
        # Apply opening (erosion followed by dilation)
        opened = cv2.morphologyEx(img_array, cv2.MORPH_OPEN, kernel, iterations=iterations)
        
        # Apply closing (dilation followed by erosion)
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, kernel, iterations=iterations)
        
        return Image.fromarray(closed)
    
    def correct_skew(self, image: Image.Image) -> Image.Image:
        """Detect and correct image rotation/skew.
        
        Args:
            image: Input PIL Image.
        
        Returns:
            Skew-corrected PIL Image.
        """
        img_array = np.array(image)
        
        # Find edges
        edges = cv2.Canny(img_array, 50, 150, apertureSize=3)
        
        # Detect lines using Hough transform
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        if lines is not None and len(lines) > 0:
            # Calculate average angle
            angles = []
            for rho, theta in lines[:, 0]:
                angle = theta * 180 / np.pi
                # Convert to rotation angle
                if angle > 90:
                    angle = angle - 180
                angles.append(angle)
            
            # Use median angle to avoid outliers
            if angles:
                median_angle = np.median(angles)
                
                # Only correct if angle is significant (> 1 degree)
                if abs(median_angle) > 1:
                    # Rotate image
                    height, width = img_array.shape
                    center = (width // 2, height // 2)
                    rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                    rotated = cv2.warpAffine(img_array, rotation_matrix, (width, height), 
                                           flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
                    return Image.fromarray(rotated)
        
        return image
    
    def enhance_image(self, image: Image.Image) -> Image.Image:
        """Enhance image contrast and sharpness.
        
        Args:
            image: Input PIL Image.
        
        Returns:
            Enhanced PIL Image.
        """
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)
        
        return image
    
    def segment_characters(self, image: Image.Image) -> List[Image.Image]:
        """Segment individual characters from CAPTCHA image.
        
        Args:
            image: Input PIL Image.
        
        Returns:
            List of character images.
        """
        img_array = np.array(image)
        
        # Find contours
        contours, _ = cv2.findContours(img_array, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Sort contours by x-coordinate (left to right)
        contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[0])
        
        characters = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter out very small contours (noise)
            if w > 5 and h > 10:
                char_img = img_array[y:y+h, x:x+w]
                characters.append(Image.fromarray(char_img))
        
        return characters
    
    def resize_image(self, image: Image.Image, scale_factor: float = 3.0) -> Image.Image:
        """Resize image for better OCR recognition.
        
        Args:
            image: Input PIL Image.
            scale_factor: Scaling factor for resizing.
        
        Returns:
            Resized PIL Image.
        """
        width, height = image.size
        new_size = (int(width * scale_factor), int(height * scale_factor))
        
        # Use LANCZOS for high-quality upscaling
        return image.resize(new_size, Image.Resampling.LANCZOS)
    
    def remove_lines(self, image: Image.Image) -> Image.Image:
        """Remove horizontal and vertical lines from image.
        
        Args:
            image: Input PIL Image.
        
        Returns:
            Image with lines removed.
        """
        img_array = np.array(image)
        
        # Create kernels for line detection
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
        
        # Detect horizontal lines
        horizontal_lines = cv2.morphologyEx(img_array, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
        
        # Detect vertical lines
        vertical_lines = cv2.morphologyEx(img_array, cv2.MORPH_OPEN, vertical_kernel, iterations=2)
        
        # Combine line masks
        lines_mask = cv2.add(horizontal_lines, vertical_lines)
        
        # Remove lines from original image
        result = cv2.subtract(img_array, lines_mask)
        
        return Image.fromarray(result)
    
    def clean_noise_pixels(self, image: Image.Image, min_area: int = 10) -> Image.Image:
        """Remove small noise pixels/regions.
        
        Args:
            image: Input PIL Image.
            min_area: Minimum area to keep (pixels).
        
        Returns:
            Cleaned PIL Image.
        """
        img_array = np.array(image)
        
        # Find connected components
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(img_array, connectivity=8)
        
        # Create mask for components to keep
        mask = np.zeros_like(img_array)
        
        for i in range(1, num_labels):  # Skip background (label 0)
            area = stats[i, cv2.CC_STAT_AREA]
            if area >= min_area:
                mask[labels == i] = 255
        
        return Image.fromarray(mask)
    
    def get_processing_info(self) -> dict:
        """Get information about current preprocessing configuration.
        
        Returns:
            Dictionary with preprocessing information.
        """
        return {
            "steps": self.processing_steps,
            "config": self.config,
            "available_steps": [
                "grayscale", "denoise", "threshold", "morphology", 
                "skew_correction", "enhance"
            ]
        }