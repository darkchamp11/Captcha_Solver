#!/usr/bin/env python3
"""Basic usage examples for CAPTCHA Solver.

This script demonstrates the most common use cases for the CAPTCHA solver,
including solving from files, URLs, and basic configuration.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from captcha_solver import CAPTCHASolver, Config


def example_solve_from_file():
    """Example: Solve CAPTCHA from image file."""
    print("=== Example 1: Solve from Image File ===")
    
    # Initialize solver with default configuration
    solver = CAPTCHASolver()
    
    # Example image path (replace with actual CAPTCHA image)
    image_path = "captcha_example.png"
    
    # Check if example image exists
    if not Path(image_path).exists():
        print(f"Example image not found: {image_path}")
        print("Please provide a CAPTCHA image file to test with.")
        return
    
    try:
        # Solve CAPTCHA
        result = solver.solve_from_file(image_path, save_processed=True)
        
        # Display results
        print(f"Image: {image_path}")
        print(f"Result: '{result}'")
        print(f"Confidence: {solver.get_confidence():.1f}%")
        
        if result:
            print("✓ CAPTCHA solved successfully!")
        else:
            print("✗ Failed to solve CAPTCHA")
    
    except Exception as e:
        print(f"Error: {e}")
    
    print()


def example_solve_from_url():
    """Example: Solve CAPTCHA from web page URL."""
    print("=== Example 2: Solve from URL ===")
    
    # Initialize solver
    solver = CAPTCHASolver()
    
    # Example URL (replace with actual URL containing CAPTCHA)
    url = "https://example.com/captcha-form"
    
    print(f"Note: This example requires a real URL with a CAPTCHA.")
    print(f"Example URL: {url}")
    print("Skipping actual URL processing in demo...")
    
    # Uncomment below to test with real URL:
    # try:
    #     result = solver.solve_from_url(url)
    #     print(f"Result: '{result}'")
    #     print(f"Confidence: {solver.get_confidence():.1f}%")
    # except Exception as e:
    #     print(f"Error: {e}")
    
    print()


def example_custom_configuration():
    """Example: Using custom configuration."""
    print("=== Example 3: Custom Configuration ===")
    
    # Create custom configuration
    custom_config = {
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
    
    # Initialize solver with custom config
    solver = CAPTCHASolver(config=custom_config)
    
    print("Custom configuration applied:")
    print(f"- Tesseract config: {custom_config['tesseract']['config']}")
    print(f"- Preprocessing steps: {custom_config['preprocessing']['steps']}")
    print(f"- Confidence threshold: {custom_config['ocr']['confidence_threshold']}%")
    
    # Test components
    print("\nTesting components with custom config:")
    tests = solver.test_components()
    for component, status in tests.items():
        status_str = "✓ PASS" if status else "✗ FAIL"
        print(f"  {component}: {status_str}")
    
    print()


def example_batch_processing():
    """Example: Batch processing multiple images."""
    print("=== Example 4: Batch Processing ===")
    
    # Initialize solver
    solver = CAPTCHASolver()
    
    # Example image paths (replace with actual CAPTCHA images)
    image_paths = [
        "captcha1.png",
        "captcha2.png",
        "captcha3.png"
    ]
    
    # Filter to only existing files
    existing_files = [path for path in image_paths if Path(path).exists()]
    
    if not existing_files:
        print("No example images found for batch processing.")
        print("Please provide CAPTCHA image files to test with.")
        print(f"Expected files: {image_paths}")
        return
    
    try:
        # Process batch
        print(f"Processing {len(existing_files)} images...")
        results = solver.solve_batch(existing_files, save_processed=True)
        
        # Display results
        print("\nBatch Results:")
        for result in results:
            status = "✓" if result["success"] else "✗"
            print(f"  {status} {Path(result['path']).name}: '{result['result']}' ({result['confidence']:.1f}%)")
        
        # Display statistics
        stats = solver.get_statistics()
        print(f"\nStatistics:")
        print(f"  Success rate: {stats['success_rate']:.1f}%")
        print(f"  Average confidence: {stats['average_confidence']:.1f}%")
    
    except Exception as e:
        print(f"Error: {e}")
    
    print()


def example_debugging():
    """Example: Debugging and inspection."""
    print("=== Example 5: Debugging and Inspection ===")
    
    # Initialize solver with debug logging
    solver = CAPTCHASolver(log_level="DEBUG")
    
    # Get system information
    print("System Information:")
    info = solver.get_system_info()
    
    print(f"  Version: {info['version']}")
    print(f"  Cache directory: {info['cache_directory']}")
    
    # Test components
    print("\nComponent Tests:")
    tests = info['component_tests']
    for component, status in tests.items():
        status_str = "✓ PASS" if status else "✗ FAIL"
        print(f"  {component}: {status_str}")
    
    # Display configuration
    print("\nCurrent Configuration:")
    config_info = info['components']['config']
    print(f"  Tesseract config: {config_info.get('tesseract', {}).get('config', 'default')}")
    print(f"  Preprocessing steps: {config_info.get('preprocessing', {}).get('steps', [])}")
    
    print()


def example_error_handling():
    """Example: Error handling and recovery."""
    print("=== Example 6: Error Handling ===")
    
    solver = CAPTCHASolver()
    
    # Test with non-existent file
    print("Testing with non-existent file:")
    try:
        result = solver.solve_from_file("non_existent_file.png")
        print(f"Result: '{result}'")
    except Exception as e:
        print(f"Expected error caught: {type(e).__name__}: {e}")
    
    # Test with invalid URL
    print("\nTesting with invalid URL:")
    try:
        result = solver.solve_from_url("invalid://url")
        print(f"Result: '{result}'")
    except Exception as e:
        print(f"Expected error caught: {type(e).__name__}: {e}")
    
    print("\n✓ Error handling working correctly")
    print()


def main():
    """Run all examples."""
    print("CAPTCHA Solver - Basic Usage Examples")
    print("=====================================")
    print()
    print("⚠️  IMPORTANT: This tool is for educational purposes only.")
    print("   Always respect website terms of service and applicable laws.")
    print()
    
    # Run examples
    example_solve_from_file()
    example_solve_from_url()
    example_custom_configuration()
    example_batch_processing()
    example_debugging()
    example_error_handling()
    
    print("Examples completed!")
    print()
    print("Next steps:")
    print("1. Provide actual CAPTCHA images to test with")
    print("2. Customize configuration for your specific use case")
    print("3. Integrate with your web automation scripts")
    print("4. Check the documentation for advanced features")


if __name__ == "__main__":
    main()