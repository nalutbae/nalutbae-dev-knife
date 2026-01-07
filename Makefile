# Makefile for Python DevKnife Toolkit

.PHONY: help install install-dev test test-cov lint format type-check clean build upload-test upload docs

# Default target
help:
	@echo "Python DevKnife Toolkit - Available commands:"
	@echo ""
	@echo "Setup:"
	@echo "  install      Install package from PyPI"
	@echo "  install-dev  Install in development mode with all dependencies"
	@echo ""
	@echo "Development:"
	@echo "  test         Run all tests"
	@echo "  test-cov     Run tests with coverage report"
	@echo "  lint         Run code linting (flake8)"
	@echo "  format       Format code with black"
	@echo "  type-check   Run type checking with mypy"
	@echo ""
	@echo "Build & Release:"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build package for distribution"
	@echo "  upload-test  Upload to Test PyPI"
	@echo "  upload       Upload to PyPI"
	@echo ""
	@echo "Utilities:"
	@echo "  docs         Generate documentation"
	@echo "  all          Run format, lint, type-check, and test"

# Installation
install:
	pip install python-devknife-toolkit

install-dev:
	pip install -e ".[dev,test]"

# Testing
test:
	pytest

test-cov:
	pytest --cov=devknife --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 devknife tests

format:
	black devknife tests scripts

type-check:
	mypy devknife

# Build and release
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python scripts/build.py

upload-test: build
	python -m twine upload --repository testpypi dist/*

upload: build
	python -m twine upload dist/*

# Documentation
docs:
	@echo "Documentation files:"
	@echo "  README.md - Main documentation"
	@echo "  SETUP.md - Setup and development guide"
	@echo "  CONTRIBUTING.md - Contribution guidelines"
	@echo "  CHANGELOG.md - Version history"

# Run all quality checks
all: format lint type-check test
	@echo "✅ All checks passed!"

# Development workflow
dev-setup: install-dev
	@echo "✅ Development environment ready!"
	@echo "Run 'make test' to verify everything works."

# Quick verification
verify:
	devknife --version
	devknife --help
	@echo "✅ Installation verified!"