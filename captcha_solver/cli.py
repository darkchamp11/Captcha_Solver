#!/usr/bin/env python3
"""Command-line interface for CAPTCHA Solver.

This module provides a command-line interface for the CAPTCHA solver,
allowing users to solve CAPTCHAs from files, URLs, or batch process multiple images.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional, List

from .solver import CAPTCHASolver
from .config import Config
from .utils import setup_logging


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser.
    
    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description="CAPTCHA Solver - Solve text-based CAPTCHAs using OCR",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --image captcha.png
  %(prog)s --url https://example.com/captcha-form
  %(prog)s --batch images/*.png
  %(prog)s --image captcha.png --config config.yaml --debug
  %(prog)s --test-components

Note: This tool is for educational and research purposes only.
Always respect website terms of service and applicable laws.
"""
    )
    
    # Input options (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument(
        "--image", "-i",
        type=str,
        help="Path to CAPTCHA image file"
    )
    input_group.add_argument(
        "--url", "-u",
        type=str,
        help="URL of web page containing CAPTCHA"
    )
    input_group.add_argument(
        "--batch", "-b",
        type=str,
        nargs="+",
        help="Process multiple image files (supports wildcards)"
    )
    
    # Configuration options
    parser.add_argument(
        "--config", "-c",
        type=str,
        help="Path to configuration file (YAML or JSON)"
    )
    
    # Output options
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file for results (JSON format for batch processing)"
    )
    parser.add_argument(
        "--save-processed",
        action="store_true",
        help="Save processed images for debugging"
    )
    
    # Logging options
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress output except results"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        help="Log file path"
    )
    
    # Utility options
    parser.add_argument(
        "--test-components",
        action="store_true",
        help="Test all components and exit"
    )
    parser.add_argument(
        "--system-info",
        action="store_true",
        help="Display system information and exit"
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    # OCR options
    parser.add_argument(
        "--tesseract-config",
        type=str,
        help="Custom Tesseract configuration string"
    )
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=60.0,
        help="Minimum confidence threshold (0-100, default: 60)"
    )
    
    # Preprocessing options
    parser.add_argument(
        "--preprocessing-steps",
        type=str,
        nargs="+",
        help="Preprocessing steps to apply",
        choices=["grayscale", "denoise", "threshold", "enhance", "morphology", "skew_correct"]
    )
    
    return parser


def setup_logging_from_args(args) -> None:
    """Setup logging based on command line arguments.
    
    Args:
        args: Parsed command line arguments.
    """
    if args.quiet:
        log_level = "ERROR"
    elif args.debug:
        log_level = "DEBUG"
    elif args.verbose:
        log_level = "INFO"
    else:
        log_level = "WARNING"
    
    setup_logging(log_level, args.log_file)


def load_config_from_args(args) -> Optional[Config]:
    """Load configuration from command line arguments.
    
    Args:
        args: Parsed command line arguments.
    
    Returns:
        Config object or None if no config specified.
    """
    config = None
    
    if args.config:
        try:
            config = Config(args.config)
        except Exception as e:
            print(f"Error loading config file {args.config}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        config = Config()
    
    # Apply command line overrides
    if args.tesseract_config:
        config.config["tesseract"]["config"] = args.tesseract_config
    
    if args.confidence_threshold:
        config.config["ocr"]["confidence_threshold"] = args.confidence_threshold
    
    if args.preprocessing_steps:
        config.config["preprocessing"]["steps"] = args.preprocessing_steps
    
    return config


def solve_single_image(solver: CAPTCHASolver, image_path: str, 
                      save_processed: bool = False) -> dict:
    """Solve a single CAPTCHA image.
    
    Args:
        solver: CAPTCHASolver instance.
        image_path: Path to image file.
        save_processed: Whether to save processed image.
    
    Returns:
        Dictionary with result information.
    """
    try:
        result = solver.solve_from_file(image_path, save_processed)
        return {
            "path": image_path,
            "result": result,
            "confidence": solver.get_confidence(),
            "success": bool(result.strip()),
            "error": None
        }
    except Exception as e:
        return {
            "path": image_path,
            "result": "",
            "confidence": 0.0,
            "success": False,
            "error": str(e)
        }


def solve_from_url(solver: CAPTCHASolver, url: str, 
                  save_processed: bool = False) -> dict:
    """Solve CAPTCHA from URL.
    
    Args:
        solver: CAPTCHASolver instance.
        url: URL to extract CAPTCHA from.
        save_processed: Whether to save processed image.
    
    Returns:
        Dictionary with result information.
    """
    try:
        result = solver.solve_from_url(url, save_processed=save_processed)
        return {
            "url": url,
            "result": result,
            "confidence": solver.get_confidence(),
            "success": bool(result.strip()),
            "error": None
        }
    except Exception as e:
        return {
            "url": url,
            "result": "",
            "confidence": 0.0,
            "success": False,
            "error": str(e)
        }


def expand_file_patterns(patterns: List[str]) -> List[str]:
    """Expand file patterns to actual file paths.
    
    Args:
        patterns: List of file patterns (may include wildcards).
    
    Returns:
        List of actual file paths.
    """
    files = []
    for pattern in patterns:
        if "*" in pattern or "?" in pattern:
            # Use glob for wildcard patterns
            from glob import glob
            files.extend(glob(pattern))
        else:
            files.append(pattern)
    
    # Filter to only existing files
    existing_files = [f for f in files if Path(f).is_file()]
    
    if not existing_files:
        print(f"No valid image files found in patterns: {patterns}", file=sys.stderr)
        sys.exit(1)
    
    return existing_files


def save_results(results: dict, output_path: str) -> None:
    """Save results to output file.
    
    Args:
        results: Results dictionary.
        output_path: Path to output file.
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"Results saved to: {output_path}")
    except Exception as e:
        print(f"Error saving results to {output_path}: {e}", file=sys.stderr)


def print_results(results: dict, quiet: bool = False) -> None:
    """Print results to console.
    
    Args:
        results: Results dictionary.
        quiet: Whether to suppress verbose output.
    """
    if "batch_results" in results:
        # Batch results
        if not quiet:
            print(f"\nBatch Processing Results:")
            print(f"Total files: {len(results['batch_results'])}")
            print(f"Successful: {results['statistics']['successful']}")
            print(f"Success rate: {results['statistics']['success_rate']:.1f}%")
            print(f"Average confidence: {results['statistics']['average_confidence']:.1f}%")
            print("\nIndividual Results:")
        
        for result in results["batch_results"]:
            if result["success"]:
                print(f"{Path(result['path']).name}: {result['result']} ({result['confidence']:.1f}%)")
            else:
                error_msg = f" - {result['error']}" if result.get('error') else ""
                print(f"{Path(result['path']).name}: FAILED{error_msg}")
    
    elif "result" in results:
        # Single result
        if results["success"]:
            if quiet:
                print(results["result"])
            else:
                print(f"Result: {results['result']}")
                print(f"Confidence: {results['confidence']:.1f}%")
        else:
            error_msg = f" - {results['error']}" if results.get('error') else ""
            print(f"FAILED{error_msg}", file=sys.stderr)
            sys.exit(1)


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging_from_args(args)
    
    # Handle utility commands
    if args.test_components or args.system_info:
        config = load_config_from_args(args)
        solver = CAPTCHASolver(config)
        
        if args.test_components:
            print("Testing components...")
            tests = solver.test_components()
            for component, status in tests.items():
                status_str = "✓ PASS" if status else "✗ FAIL"
                print(f"{component}: {status_str}")
            
            if not all(tests.values()):
                sys.exit(1)
        
        if args.system_info:
            info = solver.get_system_info()
            print(json.dumps(info, indent=2, default=str))
        
        return
    
    # Require at least one input option
    if not any([args.image, args.url, args.batch]):
        parser.print_help()
        sys.exit(1)
    
    # Load configuration
    config = load_config_from_args(args)
    
    # Initialize solver
    try:
        solver = CAPTCHASolver(config)
    except Exception as e:
        print(f"Error initializing solver: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Process input
    results = {}
    
    try:
        if args.image:
            # Single image
            results = solve_single_image(solver, args.image, args.save_processed)
        
        elif args.url:
            # URL
            results = solve_from_url(solver, args.url, args.save_processed)
        
        elif args.batch:
            # Batch processing
            file_paths = expand_file_patterns(args.batch)
            batch_results = solver.solve_batch(file_paths, args.save_processed)
            
            # Calculate statistics
            successful = sum(1 for r in batch_results if r["success"])
            total = len(batch_results)
            success_rate = (successful / total * 100) if total > 0 else 0
            avg_confidence = sum(r["confidence"] for r in batch_results if r["success"]) / max(successful, 1)
            
            results = {
                "batch_results": batch_results,
                "statistics": {
                    "total": total,
                    "successful": successful,
                    "success_rate": success_rate,
                    "average_confidence": avg_confidence
                }
            }
        
        # Save results if output file specified
        if args.output:
            save_results(results, args.output)
        
        # Print results
        print_results(results, args.quiet)
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    finally:
        # Cleanup
        try:
            solver.cleanup()
        except:
            pass


if __name__ == "__main__":
    main()