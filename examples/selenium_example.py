#!/usr/bin/env python3
"""Selenium integration example for CAPTCHA Solver.

This script demonstrates how to integrate the CAPTCHA solver with Selenium
for automated web form submission and CAPTCHA solving.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from captcha_solver import CAPTCHASolver, FormSubmitter


def setup_webdriver(headless=True):
    """Setup Chrome WebDriver with optimal settings.
    
    Args:
        headless: Whether to run browser in headless mode.
    
    Returns:
        WebDriver instance.
    """
    options = Options()
    
    if headless:
        options.add_argument("--headless")
    
    # Optimize for CAPTCHA solving
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    # Disable images for faster loading (except CAPTCHAs)
    # options.add_argument("--blink-settings=imagesEnabled=false")
    
    try:
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)
        driver.set_page_load_timeout(30)
        return driver
    except Exception as e:
        print(f"Error setting up WebDriver: {e}")
        print("Make sure Chrome and ChromeDriver are installed.")
        print("You can install ChromeDriver using: pip install webdriver-manager")
        raise


def example_basic_form_submission():
    """Example: Basic form submission with CAPTCHA solving."""
    print("=== Example 1: Basic Form Submission ===")
    
    # Initialize components
    solver = CAPTCHASolver()
    driver = setup_webdriver(headless=False)  # Show browser for demo
    submitter = FormSubmitter(driver)
    
    try:
        # Example URL (replace with actual form URL)
        form_url = "https://example.com/contact-form"
        
        print(f"Note: This example requires a real form URL with CAPTCHA.")
        print(f"Example URL: {form_url}")
        print("Skipping actual form submission in demo...")
        
        # Uncomment and modify for real usage:
        # 
        # # Navigate to form
        # driver.get(form_url)
        # print(f"Navigated to: {form_url}")
        # 
        # # Wait for page to load
        # WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.TAG_NAME, "form"))
        # )
        # 
        # # Find CAPTCHA image
        # captcha_selectors = [
        #     "img[src*='captcha']",
        #     ".captcha img",
        #     "#captcha-image",
        #     "img[alt*='captcha']"
        # ]
        # 
        # captcha_element = None
        # for selector in captcha_selectors:
        #     try:
        #         captcha_element = driver.find_element(By.CSS_SELECTOR, selector)
        #         break
        #     except NoSuchElementException:
        #         continue
        # 
        # if not captcha_element:
        #     print("CAPTCHA element not found")
        #     return
        # 
        # print("Found CAPTCHA element")
        # 
        # # Solve CAPTCHA
        # captcha_solution = solver.solve_from_element(captcha_element, driver)
        # print(f"CAPTCHA solution: '{captcha_solution}'")
        # print(f"Confidence: {solver.get_confidence():.1f}%")
        # 
        # if not captcha_solution:
        #     print("Failed to solve CAPTCHA")
        #     return
        # 
        # # Fill form data
        # form_data = {
        #     "name": "John Doe",
        #     "email": "john@example.com",
        #     "message": "Test message",
        #     "captcha": captcha_solution
        # }
        # 
        # # Submit form
        # success = submitter.submit_form(form_data, "#contact-form")
        # 
        # if success:
        #     print("✓ Form submitted successfully!")
        # else:
        #     print("✗ Form submission failed")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        driver.quit()
    
    print()


def example_login_form_with_captcha():
    """Example: Login form with CAPTCHA protection."""
    print("=== Example 2: Login Form with CAPTCHA ===")
    
    solver = CAPTCHASolver()
    driver = setup_webdriver(headless=False)
    submitter = FormSubmitter(driver)
    
    try:
        # Example login process
        print("Simulating login form with CAPTCHA...")
        
        # Create a simple HTML page for demonstration
        demo_html = """
        <!DOCTYPE html>
        <html>
        <head><title>Demo Login Form</title></head>
        <body>
            <h2>Demo Login Form</h2>
            <form id="login-form">
                <p>
                    <label>Username:</label>
                    <input type="text" name="username" required>
                </p>
                <p>
                    <label>Password:</label>
                    <input type="password" name="password" required>
                </p>
                <p>
                    <label>CAPTCHA:</label>
                    <input type="text" name="captcha" required>
                    <br>
                    <img id="captcha-image" src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==" 
                         alt="CAPTCHA" style="border: 1px solid #ccc; margin-top: 5px;">
                </p>
                <p>
                    <button type="submit">Login</button>
                </p>
            </form>
            <div id="result"></div>
        </body>
        </html>
        """
        
        # Save demo HTML to temporary file
        demo_file = Path("demo_login.html")
        demo_file.write_text(demo_html)
        
        # Navigate to demo page
        driver.get(f"file://{demo_file.absolute()}")
        print("Loaded demo login form")
        
        # Fill username and password
        driver.find_element(By.NAME, "username").send_keys("demo_user")
        driver.find_element(By.NAME, "password").send_keys("demo_password")
        
        print("Filled username and password")
        
        # Note: In real scenario, you would solve the actual CAPTCHA
        print("In real scenario, CAPTCHA would be solved here")
        driver.find_element(By.NAME, "captcha").send_keys("DEMO123")
        
        print("Demo CAPTCHA filled")
        
        # Clean up demo file
        demo_file.unlink()
        
        print("✓ Demo login form process completed")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        driver.quit()
    
    print()


def example_advanced_captcha_handling():
    """Example: Advanced CAPTCHA handling with retries and fallbacks."""
    print("=== Example 3: Advanced CAPTCHA Handling ===")
    
    # Custom configuration for better accuracy
    config = {
        "tesseract": {
            "config": "--psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ",
            "timeout": 30
        },
        "preprocessing": {
            "steps": ["grayscale", "denoise", "threshold", "enhance", "morphology"]
        },
        "ocr": {
            "confidence_threshold": 75,
            "multiple_configs": True
        }
    }
    
    solver = CAPTCHASolver(config=config)
    driver = setup_webdriver(headless=False)
    
    def solve_captcha_with_retries(captcha_element, max_retries=3):
        """Solve CAPTCHA with multiple attempts and configurations."""
        for attempt in range(max_retries):
            print(f"CAPTCHA solving attempt {attempt + 1}/{max_retries}")
            
            try:
                # Solve CAPTCHA
                result = solver.solve_from_element(captcha_element, driver)
                confidence = solver.get_confidence()
                
                print(f"Result: '{result}', Confidence: {confidence:.1f}%")
                
                # Check if result meets quality threshold
                if result and confidence >= 70:
                    print(f"✓ High confidence result accepted")
                    return result
                elif result and confidence >= 50:
                    print(f"⚠ Medium confidence result: '{result}'")
                    # Could ask user for confirmation in interactive mode
                    return result
                else:
                    print(f"✗ Low confidence result, retrying...")
                    
                    # Refresh CAPTCHA if possible
                    try:
                        refresh_button = driver.find_element(By.CSS_SELECTOR, ".captcha-refresh, #refresh-captcha")
                        refresh_button.click()
                        time.sleep(2)  # Wait for new CAPTCHA to load
                    except NoSuchElementException:
                        print("No refresh button found")
                    
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
        
        print("All attempts failed")
        return None
    
    try:
        print("Advanced CAPTCHA handling demonstration")
        print("Features:")
        print("- Multiple solving attempts")
        print("- Confidence-based validation")
        print("- CAPTCHA refresh on failure")
        print("- Custom preprocessing pipeline")
        
        # Test component configuration
        tests = solver.test_components()
        print("\nComponent tests:")
        for component, status in tests.items():
            status_str = "✓ PASS" if status else "✗ FAIL"
            print(f"  {component}: {status_str}")
        
        print("\n✓ Advanced CAPTCHA handling setup completed")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        driver.quit()
    
    print()


def example_batch_form_processing():
    """Example: Processing multiple forms with CAPTCHAs."""
    print("=== Example 4: Batch Form Processing ===")
    
    solver = CAPTCHASolver()
    
    # Simulate processing multiple forms
    form_urls = [
        "https://example1.com/form",
        "https://example2.com/contact",
        "https://example3.com/signup"
    ]
    
    results = []
    
    print(f"Simulating batch processing of {len(form_urls)} forms...")
    
    for i, url in enumerate(form_urls, 1):
        print(f"\nProcessing form {i}/{len(form_urls)}: {url}")
        
        # In real scenario, you would:
        # 1. Navigate to URL
        # 2. Fill form fields
        # 3. Solve CAPTCHA
        # 4. Submit form
        # 5. Verify submission
        
        # Simulate processing
        result = {
            "url": url,
            "status": "success" if i % 2 == 1 else "failed",
            "captcha_solved": i % 2 == 1,
            "confidence": 85.5 if i % 2 == 1 else 0.0,
            "processing_time": 2.3 + (i * 0.5)
        }
        
        results.append(result)
        print(f"  Status: {result['status']}")
        print(f"  CAPTCHA: {'✓' if result['captcha_solved'] else '✗'}")
    
    # Summary
    successful = sum(1 for r in results if r["status"] == "success")
    print(f"\nBatch Processing Summary:")
    print(f"  Total forms: {len(results)}")
    print(f"  Successful: {successful}")
    print(f"  Success rate: {successful/len(results)*100:.1f}%")
    print(f"  Average confidence: {sum(r['confidence'] for r in results if r['captcha_solved'])/max(successful, 1):.1f}%")
    
    print()


def example_error_recovery():
    """Example: Error handling and recovery strategies."""
    print("=== Example 5: Error Recovery Strategies ===")
    
    solver = CAPTCHASolver()
    
    print("Error recovery strategies:")
    print("1. Network timeouts - retry with exponential backoff")
    print("2. CAPTCHA solving failures - try different preprocessing")
    print("3. Form submission errors - validate and retry")
    print("4. Browser crashes - restart WebDriver")
    print("5. Rate limiting - implement delays and respect limits")
    
    # Demonstrate error handling
    try:
        # Simulate network error
        print("\nSimulating network error...")
        raise ConnectionError("Network timeout")
    except ConnectionError as e:
        print(f"Caught network error: {e}")
        print("Recovery: Implementing retry with backoff")
    
    try:
        # Simulate CAPTCHA solving failure
        print("\nSimulating CAPTCHA solving failure...")
        result = solver.solve_from_file("non_existent.png")
    except Exception as e:
        print(f"Caught CAPTCHA error: {type(e).__name__}")
        print("Recovery: Trying alternative preprocessing or manual intervention")
    
    print("\n✓ Error recovery strategies demonstrated")
    print()


def main():
    """Run all Selenium integration examples."""
    print("CAPTCHA Solver - Selenium Integration Examples")
    print("==============================================")
    print()
    print("⚠️  IMPORTANT: This tool is for educational purposes only.")
    print("   Always respect website terms of service and applicable laws.")
    print()
    
    # Check if Selenium is available
    try:
        from selenium import webdriver
        print("✓ Selenium is available")
    except ImportError:
        print("✗ Selenium not found. Install with: pip install selenium")
        return
    
    # Run examples
    example_basic_form_submission()
    example_login_form_with_captcha()
    example_advanced_captcha_handling()
    example_batch_form_processing()
    example_error_recovery()
    
    print("Selenium integration examples completed!")
    print()
    print("Next steps:")
    print("1. Adapt examples for your specific websites")
    print("2. Implement proper error handling and retries")
    print("3. Add rate limiting and respectful delays")
    print("4. Test thoroughly with different CAPTCHA types")
    print("5. Always comply with website terms of service")


if __name__ == "__main__":
    main()