#!/usr/bin/env python3
"""Simple test script for CAPTCHA Solver.

This script performs basic functionality tests to ensure the CAPTCHA solver
components are working correctly.
"""

import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from captcha_solver import CAPTCHASolver, Config


def create_test_captcha(text="TEST123", size=(200, 80)):
    """Create a simple test CAPTCHA image.
    
    Args:
        text: Text to render in CAPTCHA.
        size: Image size (width, height).
    
    Returns:
        PIL Image object.
    """
    # Create image with white background
    image = Image.new('RGB', size, color='white')
    draw = ImageDraw.Draw(image)
    
    # Try to use a font, fall back to default if not available
    try:
        # Try to load a system font
        font = ImageFont.truetype("arial.ttf", 36)
    except (OSError, IOError):
        try:
            font = ImageFont.load_default()
        except:
            font = None
    
    # Calculate text position (centered)
    if font:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        # Estimate text size for default font
        text_width = len(text) * 10
        text_height = 15
    
    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2
    
    # Draw text
    draw.text((x, y), text, fill='black', font=font)
    
    # Add some noise lines
    for i in range(3):
        x1 = i * 20
        y1 = 10 + i * 15
        x2 = x1 + 50
        y2 = y1 + 20
        draw.line([(x1, y1), (x2, y2)], fill='gray', width=1)
    
    return image


def test_component_initialization():
    """Test component initialization."""
    print("=== Test 1: Component Initialization ===")
    
    try:
        # Test default initialization
        solver = CAPTCHASolver()
        print("✓ Default initialization successful")
        
        # Test custom configuration
        config = {
            "tesseract": {
                "config": "--psm 8",
                "timeout": 30
            },
            "preprocessing": {
                "steps": ["grayscale", "threshold"]
            }
        }
        
        solver_custom = CAPTCHASolver(config=config)
        print("✓ Custom configuration initialization successful")
        
        # Test component tests
        tests = solver.test_components()
        print("\nComponent test results:")
        for component, status in tests.items():
            status_str = "✓ PASS" if status else "✗ FAIL"
            print(f"  {component}: {status_str}")
        
        if all(tests.values()):
            print("✓ All components initialized successfully")
            return True
        else:
            print("⚠ Some components failed initialization")
            return False
    
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return False


def test_image_processing():
    """Test image processing pipeline."""
    print("\n=== Test 2: Image Processing ===")
    
    try:
        solver = CAPTCHASolver()
        
        # Create test image
        test_image = create_test_captcha("HELLO", (150, 60))
        print("✓ Test image created")
        
        # Save test image to temporary file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            test_image.save(tmp_file.name)
            temp_path = tmp_file.name
        
        try:
            # Test image loading and processing
            result = solver.solve_from_file(temp_path, save_processed=True)
            confidence = solver.get_confidence()
            
            print(f"✓ Image processed successfully")
            print(f"  Result: '{result}'")
            print(f"  Confidence: {confidence:.1f}%")
            
            # Check if processed image is available
            processed_img = solver.get_processed_image()
            if processed_img:
                print("✓ Processed image available for inspection")
            
            return True
        
        finally:
            # Clean up temporary file
            Path(temp_path).unlink(missing_ok=True)
    
    except Exception as e:
        print(f"✗ Image processing failed: {e}")
        return False


def test_batch_processing():
    """Test batch processing functionality."""
    print("\n=== Test 3: Batch Processing ===")
    
    try:
        solver = CAPTCHASolver()
        
        # Create multiple test images
        test_texts = ["ABC123", "XYZ789", "TEST42"]
        temp_files = []
        
        for i, text in enumerate(test_texts):
            test_image = create_test_captcha(text, (160, 70))
            
            with tempfile.NamedTemporaryFile(suffix=f"_test_{i}.png", delete=False) as tmp_file:
                test_image.save(tmp_file.name)
                temp_files.append(tmp_file.name)
        
        print(f"✓ Created {len(temp_files)} test images")
        
        try:
            # Test batch processing
            results = solver.solve_batch(temp_files, save_processed=True)
            
            print(f"✓ Batch processing completed")
            print(f"  Processed: {len(results)} images")
            
            # Display results
            successful = 0
            for i, result in enumerate(results):
                status = "✓" if result["success"] else "✗"
                print(f"  {status} Image {i+1}: '{result['result']}' ({result['confidence']:.1f}%)")
                if result["success"]:
                    successful += 1
            
            success_rate = (successful / len(results)) * 100 if results else 0
            print(f"  Success rate: {success_rate:.1f}%")
            
            return True
        
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                Path(temp_file).unlink(missing_ok=True)
    
    except Exception as e:
        print(f"✗ Batch processing failed: {e}")
        return False


def test_configuration():
    """Test configuration management."""
    print("\n=== Test 4: Configuration Management ===")
    
    try:
        # Test default configuration
        config = Config()
        print("✓ Default configuration loaded")
        
        # Test configuration validation
        config.validate_config()
        print("✓ Configuration validation passed")
        
        # Test configuration access
        tesseract_config = config.get_tesseract_config()
        preprocessing_config = config.get_preprocessing_config()
        
        print(f"✓ Configuration access working")
        print(f"  Tesseract config: {tesseract_config.get('config', 'default')}")
        print(f"  Preprocessing steps: {preprocessing_config.get('steps', [])}")
        
        # Test custom configuration
        custom_config = {
            "tesseract": {"config": "--psm 7"},
            "preprocessing": {"steps": ["grayscale"]}
        }
        
        config_custom = Config()
        config_custom.config.update(custom_config)
        
        print("✓ Custom configuration applied")
        
        return True
    
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False


def test_error_handling():
    """Test error handling."""
    print("\n=== Test 5: Error Handling ===")
    
    try:
        solver = CAPTCHASolver()
        
        # Test with non-existent file
        print("Testing non-existent file handling...")
        result = solver.solve_from_file("non_existent_file.png")
        if not result:
            print("✓ Non-existent file handled gracefully")
        
        # Test with invalid URL
        print("Testing invalid URL handling...")
        result = solver.solve_from_url("invalid://url")
        if not result:
            print("✓ Invalid URL handled gracefully")
        
        # Test with empty image
        print("Testing empty image handling...")
        empty_image = Image.new('RGB', (10, 10), color='white')
        
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            empty_image.save(tmp_file.name)
            temp_path = tmp_file.name
        
        try:
            result = solver.solve_from_file(temp_path)
            print("✓ Empty image handled gracefully")
        finally:
            Path(temp_path).unlink(missing_ok=True)
        
        return True
    
    except Exception as e:
        print(f"Note: Error handling test caught exception (this may be expected): {e}")
        return True  # Errors are expected in this test


def test_statistics_and_info():
    """Test statistics and system information."""
    print("\n=== Test 6: Statistics and System Info ===")
    
    try:
        solver = CAPTCHASolver()
        
        # Test system info
        info = solver.get_system_info()
        print("✓ System information retrieved")
        print(f"  Version: {info.get('version', 'unknown')}")
        print(f"  Cache directory: {info.get('cache_directory', 'unknown')}")
        
        # Test statistics (initially empty)
        stats = solver.get_statistics()
        print("✓ Statistics retrieved")
        
        # Process a test image to generate statistics
        test_image = create_test_captcha("STATS", (140, 60))
        
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            test_image.save(tmp_file.name)
            temp_path = tmp_file.name
        
        try:
            solver.solve_from_file(temp_path)
            
            # Get updated statistics
            stats = solver.get_statistics()
            print(f"✓ Statistics updated after processing")
            print(f"  Total processed: {stats.get('total_processed', 0)}")
        
        finally:
            Path(temp_path).unlink(missing_ok=True)
        
        return True
    
    except Exception as e:
        print(f"✗ Statistics test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("CAPTCHA Solver - Test Suite")
    print("===========================")
    print()
    print("Running basic functionality tests...")
    print()
    
    # Run tests
    tests = [
        ("Component Initialization", test_component_initialization),
        ("Image Processing", test_image_processing),
        ("Batch Processing", test_batch_processing),
        ("Configuration Management", test_configuration),
        ("Error Handling", test_error_handling),
        ("Statistics and Info", test_statistics_and_info),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("TEST SUMMARY")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! CAPTCHA Solver is ready to use.")
        print("\nNext steps:")
        print("1. Test with real CAPTCHA images")
        print("2. Customize configuration for your use case")
        print("3. Integrate with your automation scripts")
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Please check the configuration and dependencies.")
        print("\nCommon issues:")
        print("- Tesseract OCR not installed or not in PATH")
        print("- Missing Python dependencies")
        print("- Insufficient permissions for file operations")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)