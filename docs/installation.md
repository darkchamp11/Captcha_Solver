# Installation Guide

This guide provides detailed instructions for installing the CAPTCHA Solver library and its dependencies.

## System Requirements

- Python 3.7 or higher
- Tesseract OCR 4.0 or higher
- Sufficient disk space for dependencies (approximately 500MB)
- Internet connection for downloading dependencies

## Installing Tesseract OCR

Tesseract OCR is a critical dependency for the CAPTCHA Solver library. Follow the instructions below to install it on your operating system.

### Windows

1. Download the installer from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer and follow the instructions
3. During installation, make sure to:
   - Select "Additional language data" if you need support for languages other than English
   - Note the installation directory (default is `C:\Program Files\Tesseract-OCR`)
4. Add the Tesseract installation directory to your PATH environment variable:
   - Right-click on "This PC" or "My Computer" and select "Properties"
   - Click on "Advanced system settings"
   - Click on "Environment Variables"
   - Under "System variables", find the "Path" variable and click "Edit"
   - Click "New" and add the Tesseract installation directory (e.g., `C:\Program Files\Tesseract-OCR`)
   - Click "OK" to close all dialogs
5. Verify the installation by opening a new Command Prompt and running:
   ```
   tesseract --version
   ```

### macOS

Using Homebrew (recommended):

```bash
brew install tesseract
```

Verify the installation:

```bash
tesseract --version
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
```

For additional language support:

```bash
sudo apt install tesseract-ocr-all
```

Or install specific language packs:

```bash
sudo apt install tesseract-ocr-eng  # English
sudo apt install tesseract-ocr-fra  # French
sudo apt install tesseract-ocr-deu  # German
# etc.
```

Verify the installation:

```bash
tesseract --version
```

### Linux (Fedora/CentOS/RHEL)

```bash
sudo dnf install tesseract
sudo dnf install tesseract-devel
```

Verify the installation:

```bash
tesseract --version
```

## Installing the CAPTCHA Solver Package

### Using pip (Recommended)

The simplest way to install the CAPTCHA Solver package is using pip:

```bash
pip install captcha-solver
```

This will install the CAPTCHA Solver package and its Python dependencies.

### Installing from Source

To install the latest development version or to contribute to the project, you can install from source:

```bash
# Clone the repository
git clone https://github.com/yourusername/captcha-solver.git
cd captcha-solver

# Install in development mode
pip install -e .
```

### Installing in a Virtual Environment (Recommended)

It's recommended to install the CAPTCHA Solver package in a virtual environment to avoid conflicts with other packages:

```bash
# Create a virtual environment
python -m venv captcha-env

# Activate the virtual environment
# On Windows:
captcha-env\Scripts\activate
# On macOS/Linux:
source captcha-env/bin/activate

# Install the package
pip install captcha-solver
```

## Installing Optional Dependencies

The CAPTCHA Solver package has several optional dependencies for advanced features:

### Machine Learning Support

```bash
pip install captcha-solver[ml]
```

This will install additional packages like TensorFlow and scikit-learn for machine learning-based CAPTCHA solving.

### Development Tools

```bash
pip install captcha-solver[dev]
```

This will install development tools like pytest, flake8, and sphinx for contributing to the project.

### All Optional Dependencies

```bash
pip install captcha-solver[all]
```

This will install all optional dependencies.

## Verifying the Installation

After installing the CAPTCHA Solver package, you can verify the installation by running:

```bash
python -c "from captcha_solver.solver import CAPTCHASolver; print(CAPTCHASolver().get_system_info())"
```

This should display system information including the Python version, Tesseract version, and installed dependencies.

You can also use the command-line interface:

```bash
captcha-solver info
```

## Troubleshooting

### Tesseract Not Found

If you encounter an error like "Tesseract not found" or "TesseractNotFoundError", it means that the CAPTCHA Solver cannot find the Tesseract executable.

**Solution:**

1. Make sure Tesseract is installed correctly
2. Verify that Tesseract is in your PATH by running `tesseract --version` in a terminal
3. If Tesseract is installed but not in your PATH, you can specify the path in your code:

```python
from captcha_solver.solver import CAPTCHASolver
from captcha_solver.config import Config

config = Config({
    "ocr": {
        "engine": "tesseract",
        "tesseract": {
            "path": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"  # Windows path
            # "path": "/usr/bin/tesseract"  # Linux/macOS path
        }
    }
})

solver = CAPTCHASolver(config)
```

### Missing Dependencies

If you encounter errors about missing dependencies, you can install them manually:

```bash
pip install requests beautifulsoup4 pillow pytesseract selenium webdriver-manager opencv-python numpy scipy scikit-image pyyaml click tqdm colorama
```

### Permission Errors

If you encounter permission errors during installation, try:

- On Windows: Run the command prompt as Administrator
- On macOS/Linux: Use `sudo` or install in a virtual environment

```bash
# Using sudo (not recommended for pip)
sudo pip install captcha-solver

# Better: Use a virtual environment
python -m venv captcha-env
source captcha-env/bin/activate  # On macOS/Linux
captcha-env\Scripts\activate  # On Windows
pip install captcha-solver
```

### SSL Certificate Errors

If you encounter SSL certificate errors during installation, you may need to update your certificates or use the `--trusted-host` option:

```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org captcha-solver
```

## Next Steps

After successfully installing the CAPTCHA Solver package, you can proceed to the [User Guide](guide.md) to learn how to use the library.