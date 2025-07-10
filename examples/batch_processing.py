#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Batch Processing Example for CAPTCHA Solver

This example demonstrates how to process multiple CAPTCHA images
in batch mode, with performance tracking and result analysis.
"""

import time
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from captcha_solver import CAPTCHASolver

# Create directories for test images and results
TEST_DIR = Path("test_captchas")
RESULT_DIR = Path("results")
TEST_DIR.mkdir(exist_ok=True)
RESULT_DIR.mkdir(exist_ok=True)


def generate_test_captchas(num_images=10):
    """Generate test CAPTCHA images for batch processing"""
    print(f"Generating {num_images} test CAPTCHA images...")
    
    # Characters to use in the CAPTCHA
    chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    image_paths = []
    ground_truth = {}
    
    # Try to use a standard font, fall back to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 36)
    except IOError:
        font = ImageFont.load_default()
    
    for i in range(num_images):
        # Generate a random CAPTCHA text (4-6 characters)
        length = random.randint(4, 6)
        captcha_text = ''.join(random.choice(chars) for _ in range(length))
        
        # Create a new image
        img = Image.new('RGB', (150, 50), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Draw the text
        draw.text((10, 10), captcha_text, fill=(0, 0, 0), font=font)
        
        # Add some noise
        for _ in range(500):
            x = random.randint(0, 149)
            y = random.randint(0, 49)
            draw.point((x, y), fill=(random.randint(0, 200), 
                                     random.randint(0, 200), 
                                     random.randint(0, 200)))
        
        # Add some lines
        for _ in range(5):
            x1 = random.randint(0, 150)
            y1 = random.randint(0, 50)
            x2 = random.randint(0, 150)
            y2 = random.randint(0, 50)
            draw.line([(x1, y1), (x2, y2)], fill=(random.randint(0, 200), 
                                                 random.randint(0, 200), 
                                                 random.randint(0, 200)))
        
        # Save the image
        image_path = TEST_DIR / f"captcha_{i+1}.png"
        img.save(image_path)
        image_paths.append(image_path)
        ground_truth[str(image_path)] = captcha_text
    
    print(f"Generated {len(image_paths)} test CAPTCHA images in {TEST_DIR}")
    return image_paths, ground_truth


def basic_batch_processing(image_paths):
    """Basic batch processing example"""
    print("\n=== Basic Batch Processing ===\n")
    
    solver = CAPTCHASolver()
    
    start_time = time.time()
    results = solver.solve_batch(image_paths)
    elapsed_time = time.time() - start_time
    
    print(f"Processed {len(results)} images in {elapsed_time:.2f} seconds")
    print(f"Average time per image: {elapsed_time/len(results):.2f} seconds")
    
    # Display results
    print("\nResults:")
    for result in results:
        print(f"  {result['path'].name}: {result['result']} (Confidence: {result['confidence']:.1f}%)")
    
    # Get statistics
    stats = solver.get_statistics()
    print(f"\nSuccess rate: {stats['success_rate']:.1f}%")
    print(f"Average confidence: {stats['average_confidence']:.1f}%")
    
    return results


def advanced_batch_processing(image_paths):
    """Advanced batch processing with custom configuration"""
    print("\n=== Advanced Batch Processing ===\n")
    
    # Custom configuration for batch processing
    config = {
        "preprocessing": {
            "steps": ["grayscale", "threshold", "denoise", "dilate"],
            "threshold": {
                "method": "adaptive",
                "block_size": 11,
                "c_value": 2
            }
        },
        "ocr": {
            "confidence_threshold": 50,
            "multiple_configs": True
        }
    }
    
    solver = CAPTCHASolver(config=config)
    
    # Process with saving intermediate results
    start_time = time.time()
    results = solver.solve_batch(
        image_paths, 
        save_processed=True,
        output_dir=RESULT_DIR
    )
    elapsed_time = time.time() - start_time
    
    print(f"Processed {len(results)} images in {elapsed_time:.2f} seconds")
    print(f"Average time per image: {elapsed_time/len(results):.2f} seconds")
    print(f"Processed images saved to {RESULT_DIR}")
    
    # Display results
    print("\nResults:")
    for result in results:
        print(f"  {result['path'].name}: {result['result']} (Confidence: {result['confidence']:.1f}%)")
    
    return results


def parallel_batch_processing(image_paths):
    """Parallel batch processing example"""
    print("\n=== Parallel Batch Processing ===\n")
    
    solver = CAPTCHASolver()
    
    # Process with parallel execution
    start_time = time.time()
    results = solver.solve_batch(
        image_paths, 
        parallel=True,
        max_workers=4  # Adjust based on your CPU cores
    )
    elapsed_time = time.time() - start_time
    
    print(f"Processed {len(results)} images in {elapsed_time:.2f} seconds using parallel processing")
    print(f"Average time per image: {elapsed_time/len(results):.2f} seconds")
    
    # Get statistics
    stats = solver.get_statistics()
    print(f"\nSuccess rate: {stats['success_rate']:.1f}%")
    print(f"Average confidence: {stats['average_confidence']:.1f}%")
    
    return results


def evaluate_accuracy(results, ground_truth):
    """Evaluate the accuracy of the CAPTCHA solver"""
    print("\n=== Accuracy Evaluation ===\n")
    
    correct = 0
    total = len(results)
    
    for result in results:
        path_str = str(result['path'])
        if path_str in ground_truth and result['result'] == ground_truth[path_str]:
            correct += 1
    
    accuracy = (correct / total) * 100 if total > 0 else 0
    print(f"Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    
    # Detailed results
    print("\nDetailed Results:")
    print("{:<20} {:<10} {:<10} {:<10}".format("Image", "Predicted", "Actual", "Correct"))
    print("-" * 50)
    
    for result in results:
        path_str = str(result['path'])
        predicted = result['result']
        actual = ground_truth.get(path_str, "Unknown")
        is_correct = "✓" if predicted == actual else "✗"
        
        print("{:<20} {:<10} {:<10} {:<10}".format(
            result['path'].name, predicted, actual, is_correct))


if __name__ == "__main__":
    print("CAPTCHA Solver - Batch Processing Examples")
    print("=" * 50)
    
    # Generate test CAPTCHA images
    image_paths, ground_truth = generate_test_captchas(num_images=10)
    
    # Run the examples
    basic_results = basic_batch_processing(image_paths)
    advanced_results = advanced_batch_processing(image_paths)
    parallel_results = parallel_batch_processing(image_paths)
    
    # Evaluate accuracy
    evaluate_accuracy(basic_results, ground_truth)
    
    print("\n=== Examples Completed ===\n")
    print(f"Test images are in: {TEST_DIR}")
    print(f"Processed images are in: {RESULT_DIR}")