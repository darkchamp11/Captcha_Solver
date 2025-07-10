#!/usr/bin/env python3
"""Setup script for CAPTCHA Solver package."""

import os
from setuptools import setup, find_packages

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="captcha-solver",
    version="1.0.0",
    author="CAPTCHA Solver Team",
    author_email="contact@captchasolver.dev",
    description="A comprehensive Python-based CAPTCHA solving toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/captcha-solver",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/captcha-solver/issues",
        "Documentation": "https://github.com/yourusername/captcha-solver/docs",
        "Source Code": "https://github.com/yourusername/captcha-solver",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Security",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
            "pre-commit>=2.20.0",
        ],
        "ml": [
            "tensorflow>=2.11.0",
            "torch>=1.13.0",
            "torchvision>=0.14.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
            "myst-parser>=0.18.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "captcha-solver=captcha_solver.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "captcha_solver": [
            "config/*.yaml",
            "config/*.json",
            "data/*.txt",
        ],
    },
    keywords=[
        "captcha",
        "ocr",
        "image-processing",
        "computer-vision",
        "selenium",
        "tesseract",
        "automation",
        "web-scraping",
        "security-testing",
        "opencv",
    ],
    license="MIT",
    zip_safe=False,
)