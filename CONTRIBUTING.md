# Contributing to Python DevKnife Toolkit

Thank you for your interest in contributing to Python DevKnife Toolkit! This document provides guidelines and information for contributors.

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setting up the Development Environment

1. Clone the repository:
```bash
git clone https://github.com/devknife-team/python-devknife-toolkit.git
cd python-devknife-toolkit
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the package in development mode with all dependencies:
```bash
pip install -e ".[dev]"
```

4. Verify the installation:
```bash
devknife --help
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=devknife

# Run specific test file
pytest tests/test_specific.py

# Run property-based tests
pytest tests/ -k "property"
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Format code with Black
black devknife tests

# Check code style with flake8
flake8 devknife tests

# Type checking with mypy
mypy devknife
```

### Adding New Utilities

To add a new utility module:

1. Create the utility class in `devknife/utils/`:
```python
from devknife.core.interfaces import UtilityModule
from devknife.core.models import ProcessingResult
from typing import Any, Dict

class YourUtility(UtilityModule):
    def process(self, input_data: Any, options: Dict[str, Any]) -> ProcessingResult:
        # Implement your utility logic here
        pass
    
    def get_help(self) -> str:
        return "Help text for your utility"
    
    def validate_input(self, input_data: Any) -> bool:
        # Validate input data
        return True
```

2. Register the utility in the command router
3. Add CLI commands in `devknife/cli/main.py`
4. Add TUI interface support if applicable
5. Write comprehensive tests including property-based tests
6. Update documentation

### Testing Guidelines

#### Unit Tests
- Test specific functionality with known inputs and expected outputs
- Test error conditions and edge cases
- Use descriptive test names that explain what is being tested

#### Property-Based Tests
- Use Hypothesis for property-based testing
- Test universal properties that should hold for all valid inputs
- Each property test should run at least 100 iterations
- Tag tests with the corresponding design document property

Example property-based test:
```python
from hypothesis import given, strategies as st
import pytest

@given(st.text())
def test_base64_round_trip_property(input_text):
    """
    **Feature: python-devknife-toolkit, Property 1: Base64 인코딩 왕복**
    **Validates: Requirements 1.2**
    """
    from devknife.utils.encoding_utility import Base64EncoderDecoder
    
    encoder = Base64EncoderDecoder()
    encoded = encoder.encode(input_text)
    decoded = encoder.decode(encoded)
    
    assert decoded == input_text
```

### Documentation

- Update README.md with new features and usage examples
- Add docstrings to all public functions and classes
- Update CHANGELOG.md with your changes
- Include practical examples in documentation

### Commit Guidelines

We follow conventional commit format:

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test additions or modifications
- `refactor:` for code refactoring
- `perf:` for performance improvements
- `chore:` for maintenance tasks

Example:
```
feat: add GraphQL query formatter utility

- Implement GraphQL query parsing and formatting
- Add CLI command for GraphQL formatting
- Include comprehensive tests and documentation
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes following the development guidelines
4. Add or update tests as needed
5. Update documentation
6. Ensure all tests pass and code quality checks pass
7. Commit your changes with descriptive commit messages
8. Push to your fork: `git push origin feature/your-feature-name`
9. Create a pull request with a clear description of your changes

### Pull Request Checklist

- [ ] Tests pass (`pytest`)
- [ ] Code is formatted (`black devknife tests`)
- [ ] Code style is correct (`flake8 devknife tests`)
- [ ] Type checking passes (`mypy devknife`)
- [ ] Documentation is updated
- [ ] CHANGELOG.md is updated
- [ ] Commit messages follow conventional format

## Code Style

- Follow PEP 8 Python style guide
- Use Black for code formatting (line length: 88 characters)
- Use type hints for all function parameters and return values
- Write descriptive docstrings for all public functions and classes
- Keep functions focused and single-purpose
- Use meaningful variable and function names

## Architecture Guidelines

- Follow the existing modular architecture
- Keep utilities independent and reusable
- Use the established interfaces and data models
- Maintain separation between CLI, TUI, and core logic
- Handle errors gracefully with user-friendly messages
- Optimize for both small and large data processing

## Getting Help

If you need help or have questions:

1. Check the existing documentation and examples
2. Look at similar implementations in the codebase
3. Open an issue for discussion
4. Join our community discussions

## License

By contributing to Python DevKnife Toolkit, you agree that your contributions will be licensed under the MIT License.