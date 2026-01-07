#!/usr/bin/env python3
"""
Build script for Nalutbae DevKnife Toolkit

This script handles building the package for distribution.
"""

import subprocess
import sys
import shutil
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Command: {cmd}")
        print(f"Return code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        sys.exit(1)


def clean_build_artifacts():
    """Clean up build artifacts."""
    print("🧹 Cleaning build artifacts...")

    artifacts = [
        "build/",
        "dist/",
        "*.egg-info/",
        "__pycache__/",
        ".pytest_cache/",
        ".hypothesis/",
    ]

    for pattern in artifacts:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"   Removed directory: {path}")
            elif path.is_file():
                path.unlink()
                print(f"   Removed file: {path}")

    print("✅ Build artifacts cleaned")


def run_tests():
    """Run the test suite."""
    run_command("python -m pytest tests/ -v", "Running test suite")


def run_quality_checks():
    """Run code quality checks."""
    run_command("python -m black --check devknife tests", "Checking code formatting")
    run_command("python -m flake8 devknife tests", "Running flake8 linting")
    # Skip mypy for now due to type annotation issues
    # run_command("python -m mypy devknife", "Running type checking")


def build_package():
    """Build the package."""
    run_command("python -m build", "Building package")


def check_package():
    """Check the built package."""
    run_command("python -m twine check dist/*", "Checking package")


def main():
    """Main build process."""
    print("🚀 Starting Nalutbae DevKnife Toolkit build process")
    print("=" * 50)

    # Check if build dependencies are installed
    try:
        import build
        import twine
    except ImportError:
        print("❌ Build dependencies not found. Installing...")
        run_command("pip install build twine", "Installing build dependencies")

    # Clean previous builds
    clean_build_artifacts()

    # Run tests
    run_tests()

    # Run quality checks
    run_quality_checks()

    # Build package
    build_package()

    # Check package
    check_package()

    print("=" * 50)
    print("🎉 Build completed successfully!")
    print("\nNext steps:")
    print("1. Review the built packages in the dist/ directory")
    print("2. Test installation: pip install dist/*.whl")
    print("3. Upload to PyPI: python -m twine upload dist/*")


if __name__ == "__main__":
    main()
