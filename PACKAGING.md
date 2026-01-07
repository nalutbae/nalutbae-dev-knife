# Packaging and Distribution Guide

This document provides comprehensive information about the packaging and distribution setup for Python DevKnife Toolkit.

## Package Structure

The project follows Python packaging best practices with the following structure:

```
python-devknife-toolkit/
├── devknife/                    # Main package
│   ├── __init__.py
│   ├── main.py                  # Entry point
│   ├── cli/                     # CLI interface
│   ├── tui/                     # TUI interface
│   ├── core/                    # Core functionality
│   └── utils/                   # Utility modules
├── tests/                       # Test suite
├── scripts/                     # Build and release scripts
├── .github/                     # GitHub workflows and templates
├── pyproject.toml              # Package configuration
├── README.md                   # Main documentation
├── CHANGELOG.md                # Version history
├── CONTRIBUTING.md             # Contribution guidelines
├── SETUP.md                    # Setup instructions
├── LICENSE                     # MIT License
├── MANIFEST.in                 # Package manifest
├── Makefile                    # Development commands
├── Dockerfile                  # Container setup
├── docker-compose.yml          # Container orchestration
└── .flake8                     # Linting configuration
```

## Package Configuration

### pyproject.toml

The main configuration file contains:

- **Package metadata**: name, version, description, authors
- **Dependencies**: runtime and development dependencies
- **Build system**: setuptools configuration
- **Entry points**: CLI command registration
- **Tool configurations**: pytest, black, mypy settings
- **URLs**: project links and documentation

Key sections:

```toml
[project]
name = "python-devknife-toolkit"
version = "0.1.0"
description = "Python으로 구현된 일상적인 개발자 유틸리티를 통합한 올인원 터미널 툴킷"

[project.scripts]
devknife = "devknife.main:main"

[project.urls]
Homepage = "https://github.com/devknife-team/python-devknife-toolkit"
Repository = "https://github.com/devknife-team/python-devknife-toolkit.git"
Issues = "https://github.com/devknife-team/python-devknife-toolkit/issues"
```

### MANIFEST.in

Specifies which files to include in the source distribution:

- Documentation files (README, LICENSE, CHANGELOG)
- Configuration files (pyproject.toml)
- Package source code
- CSS files for TUI
- Excludes development and cache files

## Build System

### Automated Build Script

`scripts/build.py` provides a comprehensive build process:

1. **Clean artifacts**: Remove previous build files
2. **Run tests**: Execute the full test suite
3. **Code quality**: Check formatting and linting
4. **Build package**: Create wheel and source distributions
5. **Validate package**: Check package integrity

Usage:
```bash
python scripts/build.py
```

### Manual Build

```bash
# Install build dependencies
pip install build twine

# Build package
python -m build

# Check package
python -m twine check dist/*
```

## Distribution Files

The build process creates two distribution formats:

1. **Wheel** (`.whl`): Binary distribution for faster installation
2. **Source Distribution** (`.tar.gz`): Source code archive

Both are created in the `dist/` directory.

## Release Process

### Automated Release

`scripts/release.py` handles the complete release workflow:

1. **Version bumping**: Increment version numbers
2. **Changelog update**: Add release notes
3. **Git operations**: Commit changes and create tags
4. **Build and upload**: Create distributions and upload to PyPI

Usage:
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

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with release notes
3. **Run quality checks**:
   ```bash
   pytest
   black --check devknife tests
   flake8 devknife tests
   ```
4. **Build package**:
   ```bash
   python scripts/build.py
   ```
5. **Create git tag**:
   ```bash
   git add .
   git commit -m "chore: bump version to X.Y.Z"
   git tag -a vX.Y.Z -m "Release version X.Y.Z"
   ```
6. **Upload to PyPI**:
   ```bash
   python -m twine upload dist/*
   ```
7. **Push changes**:
   ```bash
   git push
   git push --tags
   ```

## PyPI Distribution

### Test PyPI

For testing releases:

```bash
# Upload to Test PyPI
python -m twine upload --repository testpypi dist/*

# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ python-devknife-toolkit
```

### Production PyPI

For production releases:

```bash
# Upload to PyPI
python -m twine upload dist/*

# Install from PyPI
pip install python-devknife-toolkit
```

## Installation Methods

### From PyPI (Recommended for Users)

```bash
# Latest stable version
pip install python-devknife-toolkit

# Specific version
pip install python-devknife-toolkit==0.1.0

# With optional dependencies
pip install python-devknife-toolkit[dev]
```

### From Source (For Development)

```bash
# Clone repository
git clone https://github.com/devknife-team/python-devknife-toolkit.git
cd python-devknife-toolkit

# Install in development mode
pip install -e ".[dev]"

# Or use install script
python scripts/install.py --dev
```

### From Wheel File

```bash
# Download and install wheel
pip install python_devknife_toolkit-0.1.0-py3-none-any.whl
```

## CI/CD Pipeline

### GitHub Actions

`.github/workflows/ci.yml` provides automated CI/CD:

- **Testing**: Run tests on multiple Python versions and OS
- **Quality checks**: Code formatting, linting, type checking
- **Build**: Create distribution packages
- **Deploy**: Automatic deployment to Test PyPI and PyPI

Triggers:
- Push to main/develop branches
- Pull requests to main
- Release publications

### Workflow Steps

1. **Test Matrix**: Python 3.8-3.12 on Ubuntu, Windows, macOS
2. **Quality Gates**: All checks must pass
3. **Build Artifacts**: Create and validate packages
4. **Test Deployment**: Upload to Test PyPI on main branch
5. **Production Deployment**: Upload to PyPI on releases

## Development Tools

### Makefile

Provides convenient commands:

```bash
make install-dev    # Install development dependencies
make test          # Run tests
make format        # Format code
make lint          # Run linting
make build         # Build package
make clean         # Clean artifacts
```

### Docker Support

For containerized development:

```bash
# Build development container
docker-compose build devknife-dev

# Run development environment
docker-compose run devknife-dev

# Run specific commands
docker-compose run devknife-dev make test
```

## Package Metadata

### Classification

The package is classified as:

- **Development Status**: Beta
- **Environment**: Console/Terminal
- **Intended Audience**: Developers, System Administrators
- **License**: MIT
- **Programming Language**: Python 3.8+
- **Topic**: Software Development, System Administration, Utilities

### Keywords

Optimized for discoverability:
- developer-tools, cli, tui, utilities
- encoding, json, xml, yaml, base64
- csv, markdown, uuid, hash
- terminal, devtools

## Quality Assurance

### Code Quality Tools

- **Black**: Code formatting (88 character line length)
- **Flake8**: Linting with custom configuration
- **MyPy**: Static type checking (lenient for now)
- **Pytest**: Testing framework with coverage

### Testing Strategy

- **Unit Tests**: Specific functionality testing
- **Property-Based Tests**: Universal property validation
- **Integration Tests**: Component interaction testing
- **CLI Tests**: Command-line interface testing

### Coverage Requirements

- Minimum test coverage maintained
- Property-based tests for critical functionality
- Integration tests for user workflows

## Security Considerations

### Package Security

- No external network calls for data processing
- All processing performed locally
- Minimal dependencies to reduce attack surface
- Regular dependency updates

### Distribution Security

- Package signing for PyPI uploads
- Secure CI/CD pipeline with secrets management
- Automated security scanning in GitHub Actions

## Troubleshooting

### Common Build Issues

1. **Missing dependencies**: Install with `pip install -e ".[dev]"`
2. **Permission errors**: Use virtual environment
3. **Version conflicts**: Clean install in fresh environment

### Distribution Issues

1. **Upload failures**: Check PyPI credentials and package name
2. **Installation failures**: Verify package integrity
3. **Import errors**: Check entry point configuration

### Getting Help

- Check [SETUP.md](SETUP.md) for detailed setup instructions
- Review [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
- Open issues on GitHub for specific problems
- Check existing documentation and examples

## Future Improvements

### Planned Enhancements

- Enhanced type checking with stricter mypy configuration
- Additional distribution formats (conda, snap, etc.)
- Automated security scanning and dependency updates
- Performance benchmarking in CI/CD
- Multi-architecture builds for different platforms

### Maintenance

- Regular dependency updates
- Security patch releases
- Documentation improvements
- Community feedback integration