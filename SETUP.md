# Setup Guide for Python DevKnife Toolkit

This guide provides detailed instructions for setting up Python DevKnife Toolkit for development, testing, and distribution.

## Table of Contents

- [Quick Installation](#quick-installation)
- [Development Setup](#development-setup)
- [Building and Distribution](#building-and-distribution)
- [Testing](#testing)
- [Release Process](#release-process)
- [Troubleshooting](#troubleshooting)

## Quick Installation

### From PyPI (Recommended for Users)

```bash
# Install the latest stable version
pip install nalutbae-dev-knife

# Verify installation
devknife --version
devknife --help
```

### From Source (For Development)

```bash
# Clone the repository
git clone https://github.com/nalutebae/nalutbae-dev-knife.git
cd nalutbae-dev-knife

# Run the installation script
python scripts/install.py --dev

# Or manually install in development mode
pip install -e ".[dev]"
```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- git (for version control)

### Step-by-Step Development Setup

1. **Clone and Navigate**
   ```bash
   git clone https://github.com/nalutebae/nalutbae-dev-knife.git
   cd nalutbae-dev-knife
   ```

2. **Create Virtual Environment** (Recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   # Using the install script
   python scripts/install.py --dev --test
   
   # Or manually
   pip install -e ".[dev,test]"
   ```

4. **Verify Development Setup**
   ```bash
   # Run tests
   pytest
   
   # Check code formatting
   black --check devknife tests
   
   # Run linting
   flake8 devknife tests
   
   # Type checking
   mypy devknife
   
   # Test the CLI
   devknife --help
   ```

### Development Tools

The development environment includes:

- **pytest**: Testing framework
- **hypothesis**: Property-based testing
- **black**: Code formatting
- **flake8**: Code linting
- **mypy**: Static type checking
- **build**: Package building
- **twine**: PyPI uploading

## Building and Distribution

### Building the Package

```bash
# Using the build script (recommended)
python scripts/build.py

# Or manually
python -m build
```

This will create distribution files in the `dist/` directory:
- `python_devknife_toolkit-X.Y.Z-py3-none-any.whl` (wheel format)
- `nalutbae-dev-knife-X.Y.Z.tar.gz` (source distribution)

### Testing the Built Package

```bash
# Install from local wheel
pip install dist/python_devknife_toolkit-*.whl

# Test installation
devknife --version
devknife base64 'test'
```

### Distribution to PyPI

#### Test PyPI (Recommended for Testing)

```bash
# Upload to Test PyPI
python -m twine upload --repository testpypi dist/*

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ nalutbae-dev-knife
```

#### Production PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*

# Install from PyPI
pip install nalutbae-dev-knife
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=devknife --cov-report=html

# Run specific test categories
pytest tests/core/  # Core functionality tests
pytest tests/utils/  # Utility tests
pytest -k "property"  # Property-based tests only
pytest -k "not property"  # Unit tests only

# Run tests with verbose output
pytest -v

# Run tests and stop on first failure
pytest -x
```

### Test Categories

1. **Unit Tests**: Test specific functionality with known inputs
2. **Property-Based Tests**: Test universal properties with generated inputs
3. **Integration Tests**: Test component interactions
4. **CLI Tests**: Test command-line interface
5. **TUI Tests**: Test terminal user interface

### Writing Tests

#### Unit Tests
```python
def test_base64_encoding():
    """Test Base64 encoding with known input."""
    from devknife.utils.encoding_utility import Base64EncoderDecoder
    
    encoder = Base64EncoderDecoder()
    result = encoder.encode("Hello World!")
    assert result == "SGVsbG8gV29ybGQh"
```

#### Property-Based Tests
```python
from hypothesis import given, strategies as st

@given(st.text())
def test_base64_round_trip_property(input_text):
    """
    **Feature: nalutbae-dev-knife, Property 1: Base64 인코딩 왕복**
    **Validates: Requirements 1.2**
    """
    from devknife.utils.encoding_utility import Base64EncoderDecoder
    
    encoder = Base64EncoderDecoder()
    encoded = encoder.encode(input_text)
    decoded = encoder.decode(encoded)
    
    assert decoded == input_text
```

## Release Process

### Automated Release

```bash
# Patch release (0.1.0 -> 0.1.1)
python scripts/release.py patch

# Minor release (0.1.0 -> 0.2.0)
python scripts/release.py minor

# Major release (0.1.0 -> 1.0.0)
python scripts/release.py major

# Test release to Test PyPI
python scripts/release.py patch --test-pypi
```

### Manual Release Steps

1. **Update Version**
   - Edit version in `pyproject.toml`
   - Update `CHANGELOG.md`

2. **Run Quality Checks**
   ```bash
   pytest
   black --check devknife tests
   flake8 devknife tests
   mypy devknife
   ```

3. **Build Package**
   ```bash
   python scripts/build.py
   ```

4. **Create Git Tag**
   ```bash
   git add .
   git commit -m "chore: bump version to X.Y.Z"
   git tag -a vX.Y.Z -m "Release version X.Y.Z"
   ```

5. **Upload to PyPI**
   ```bash
   python -m twine upload dist/*
   ```

6. **Push Changes**
   ```bash
   git push
   git push --tags
   ```

## Troubleshooting

### Common Issues

#### Import Errors
```bash
# If you get import errors after installation
pip install --force-reinstall nalutbae-dev-knife

# For development mode
pip install -e . --force-reinstall
```

#### Build Failures
```bash
# Clean build artifacts
rm -rf build/ dist/ *.egg-info/

# Reinstall build dependencies
pip install --upgrade build twine

# Try building again
python scripts/build.py
```

#### Test Failures
```bash
# Update test dependencies
pip install --upgrade pytest hypothesis

# Clear pytest cache
rm -rf .pytest_cache/

# Run tests with verbose output
pytest -v --tb=short
```

#### Permission Errors on Scripts
```bash
# Make scripts executable
chmod +x scripts/*.py

# Or run with python explicitly
python scripts/build.py
```

### Environment Issues

#### Python Version Compatibility
```bash
# Check Python version
python --version

# If using wrong version, use specific version
python3.8 -m pip install nalutbae-dev-knife
```

#### Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf venv/
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Getting Help

1. Check the [README.md](README.md) for usage examples
2. Review the [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
3. Look at existing tests for implementation examples
4. Open an issue on GitHub for specific problems

## Configuration Files

### pyproject.toml
Main configuration file containing:
- Package metadata
- Dependencies
- Build configuration
- Tool configurations (pytest, black, mypy)

### MANIFEST.in
Specifies which files to include in the source distribution.

### Scripts Directory
- `build.py`: Automated build process
- `release.py`: Automated release process
- `install.py`: Installation helper

## Best Practices

1. **Always use virtual environments** for development
2. **Run tests before committing** changes
3. **Follow conventional commit messages**
4. **Update documentation** with new features
5. **Test on multiple Python versions** if possible
6. **Use Test PyPI** before production releases
7. **Keep dependencies minimal** and up-to-date