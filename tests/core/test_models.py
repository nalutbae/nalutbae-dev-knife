"""
Tests for core data models.
"""

import pytest
from devknife.core.models import Command, InputData, ProcessingResult, Config, InputSource


class TestCommand:
    """Tests for Command model."""
    
    def test_valid_command_creation(self):
        """Test creating a valid command."""
        cmd = Command(
            name="base64",
            description="Base64 encoding/decoding",
            category="encoding",
            module="devknife.utils.encoding"
        )
        assert cmd.name == "base64"
        assert cmd.description == "Base64 encoding/decoding"
        assert cmd.category == "encoding"
        assert cmd.module == "devknife.utils.encoding"
        assert cmd.cli_enabled is True
        assert cmd.tui_enabled is True
    
    def test_command_validation(self):
        """Test command validation."""
        with pytest.raises(ValueError, match="Command name cannot be empty"):
            Command(name="", description="test", category="test", module="test")
        
        with pytest.raises(ValueError, match="Command description cannot be empty"):
            Command(name="test", description="", category="test", module="test")


class TestInputData:
    """Tests for InputData model."""
    
    def test_string_input_data(self):
        """Test creating InputData with string content."""
        data = InputData(content="test content", source=InputSource.ARGS)
        assert data.content == "test content"
        assert data.source == InputSource.ARGS
        assert data.encoding == "utf-8"
        assert data.as_string() == "test content"
    
    def test_bytes_input_data(self):
        """Test creating InputData with bytes content."""
        content = "test content".encode("utf-8")
        data = InputData(content=content, source=InputSource.FILE)
        assert data.content == content
        assert data.as_string() == "test content"
        assert data.as_bytes() == content
    
    def test_input_data_validation(self):
        """Test InputData validation."""
        with pytest.raises(ValueError, match="Content cannot be None"):
            InputData(content=None, source=InputSource.ARGS)


class TestProcessingResult:
    """Tests for ProcessingResult model."""
    
    def test_successful_result(self):
        """Test creating a successful processing result."""
        result = ProcessingResult(success=True, output="processed data")
        assert result.success is True
        assert result.output == "processed data"
        assert result.error_message is None
        assert result.warnings == []
    
    def test_failed_result(self):
        """Test creating a failed processing result."""
        result = ProcessingResult(success=False, output=None, error_message="Processing failed")
        assert result.success is False
        assert result.error_message == "Processing failed"
    
    def test_result_validation(self):
        """Test ProcessingResult validation."""
        with pytest.raises(ValueError, match="Error message is required when success is False"):
            ProcessingResult(success=False, output=None)
    
    def test_add_warning(self):
        """Test adding warnings to result."""
        result = ProcessingResult(success=True, output="data")
        result.add_warning("This is a warning")
        assert "This is a warning" in result.warnings
        
        # Test duplicate warning prevention
        result.add_warning("This is a warning")
        assert result.warnings.count("This is a warning") == 1


class TestConfig:
    """Tests for Config model."""
    
    def test_default_config(self):
        """Test creating config with default values."""
        config = Config()
        assert config.default_encoding == "utf-8"
        assert config.max_file_size == 100 * 1024 * 1024
        assert config.output_format == "auto"
        assert config.tui_theme == "default"
    
    def test_config_validation(self):
        """Test config validation."""
        with pytest.raises(ValueError, match="Max file size must be positive"):
            Config(max_file_size=-1)
        
        with pytest.raises(ValueError, match="Default encoding cannot be empty"):
            Config(default_encoding="")
    
    def test_validate_file_size(self):
        """Test file size validation."""
        config = Config(max_file_size=1000)
        assert config.validate_file_size(500) is True
        assert config.validate_file_size(1000) is True
        assert config.validate_file_size(1001) is False
        assert config.validate_file_size(-1) is False