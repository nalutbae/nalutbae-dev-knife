#!/usr/bin/env python3
"""
Installation script for Python DevKnife Toolkit

This script provides an easy way to install the toolkit with all dependencies.
"""

import subprocess
import sys
import os
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
        return None


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(
            f"❌ Python 3.8+ is required. Current version: {version.major}.{version.minor}.{version.micro}"
        )
        sys.exit(1)
    print(
        f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible"
    )


def check_pip():
    """Check if pip is available."""
    result = run_command("pip --version", "Checking pip availability")
    if result is None:
        print("❌ pip is not available. Please install pip first.")
        sys.exit(1)


def install_package(dev_mode=False, test_dependencies=False):
    """Install the package."""
    if dev_mode:
        # Development installation
        if test_dependencies:
            cmd = 'pip install -e ".[dev,test]"'
            description = "Installing in development mode with all dependencies"
        else:
            cmd = 'pip install -e ".[dev]"'
            description = "Installing in development mode"
    else:
        # Regular installation
        if Path("pyproject.toml").exists():
            # Local installation
            cmd = "pip install ."
            description = "Installing from local source"
        else:
            # PyPI installation
            cmd = "pip install nalutbae-dev-knife"
            description = "Installing from PyPI"

    result = run_command(cmd, description)
    return result is not None


def verify_installation():
    """Verify that the installation was successful."""
    print("🔍 Verifying installation...")

    # Check if devknife command is available
    result = run_command("devknife --version", "Checking devknife command")
    if result is None:
        print("❌ Installation verification failed")
        return False

    # Check if we can import the package
    try:
        import devknife

        print("✅ Package import successful")
    except ImportError as e:
        print(f"❌ Package import failed: {e}")
        return False

    print("✅ Installation verified successfully")
    return True


def show_usage_examples():
    """Show basic usage examples."""
    print("\n" + "=" * 50)
    print("🎉 Installation completed successfully!")
    print("=" * 50)
    print("\n📚 Quick Start Examples:")
    print("\n1. Get help:")
    print("   devknife --help")

    print("\n2. Base64 encoding:")
    print("   devknife base64 'Hello World!'")

    print("\n3. JSON formatting:")
    print('   devknife json \'{"name":"John","age":30}\'')

    print("\n4. Start TUI mode:")
    print("   devknife")

    print("\n5. List all available commands:")
    print("   devknife list-commands")

    print("\n📖 For more examples and documentation:")
    print("   https://github.com/nalutebae/nalutbae-dev-knife#readme")


def main():
    """Main installation process."""
    print("🚀 Python DevKnife Toolkit Installation")
    print("=" * 40)

    # Parse command line arguments
    dev_mode = "--dev" in sys.argv
    test_deps = "--test" in sys.argv
    skip_verify = "--skip-verify" in sys.argv

    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python scripts/install.py [options]")
        print("\nOptions:")
        print("  --dev          Install in development mode")
        print("  --test         Include test dependencies")
        print("  --skip-verify  Skip installation verification")
        print("  --help, -h     Show this help message")
        return

    # Check prerequisites
    check_python_version()
    check_pip()

    # Install package
    success = install_package(dev_mode, test_deps)
    if not success:
        print("❌ Installation failed")
        sys.exit(1)

    # Verify installation
    if not skip_verify:
        if not verify_installation():
            print("❌ Installation verification failed")
            sys.exit(1)

    # Show usage examples
    show_usage_examples()


if __name__ == "__main__":
    main()
