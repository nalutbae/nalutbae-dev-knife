"""
Tests for the input/output handling components.
"""

import json
import tempfile
import pytest
from pathlib import Path
from io import StringIO
from unittest.mock import patch, MagicMock

from devknife.core.io_handler import InputHandler, OutputFormatter, ErrorHandler, OutputFormat
from devknife.core.models import InputData, InputSource, Config


class TestInputHandler:
    """Test cases for InputHandler class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config()
        self.handler = InputHandler(self.config)
    
    def test_read_from_args_success(self):
        """Test successful reading from command line arguments."""
        args = ["hello", "world", "test"]
        result = self.handler.read_from_args(args)
        
        assert result.content == "hello world test"
        assert result.source == InputSource.ARGS
        assert result.encoding == self.config.default_encoding
        assert result.metadata["arg_count"] == 3
    
    def test_read_from_args_empty(self):
        """Test reading from empty arguments raises error."""
        with pytest.raises(ValueError, match="No arguments provided"):
            self.handler.read_from_args([])
    
    def test_read_from_args_none(self):
        """Test reading from None arguments raises error."""
        with pytest.raises(ValueError, match="No arguments provided"):
            self.handler.read_from_args(None)
    
    def test_read_from_stdin_success(self):
        """Test successful reading from stdin."""
        mock_stdin = StringIO("test input data")
        mock_stdin.isatty = MagicMock(return_value=False)
        
        result = self.handler.read_from_stdin(mock_stdin)
        
        assert result.content == "test input data"
        assert result.source == InputSource.STDIN
        assert result.encoding == self.config.default_encoding
        assert result.metadata["length"] == len("test input data")
    
    def test_read_from_stdin_tty(self):
        """Test reading from stdin when it's a TTY raises error."""
        mock_stdin = StringIO("")
        mock_stdin.isatty = MagicMock(return_value=True)
        
        with pytest.raises(ValueError, match="No data available from stdin"):
            self.handler.read_from_stdin(mock_stdin)
    
    def test_read_from_stdin_empty(self):
        """Test reading empty stdin raises error."""
        mock_stdin = StringIO("")
        mock_stdin.isatty = MagicMock(return_value=False)
        
        with pytest.raises(ValueError, match="Empty input from stdin"):
            self.handler.read_from_stdin(mock_stdin)
    
    def test_read_from_file_success(self):
        """Test successful reading from file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write("test file content")
            temp_path = f.name
        
        try:
            result = self.handler.read_from_file(temp_path)
            
            assert result.content == "test file content"
            assert result.source == InputSource.FILE
            assert "file_path" in result.metadata
            assert "file_size" in result.metadata
            assert result.metadata["file_size"] > 0
        finally:
            Path(temp_path).unlink()
    
    def test_read_from_file_not_found(self):
        """Test reading from non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            self.handler.read_from_file("non_existent_file.txt")
    
    def test_read_from_file_empty(self):
        """Test reading from empty file raises error."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="File is empty"):
                self.handler.read_from_file(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_detect_encoding_utf8(self):
        """Test encoding detection for UTF-8 content."""
        content = "Hello, 世界!".encode('utf-8')
        encoding = self.handler.detect_encoding(content)
        assert encoding in ['utf-8', 'UTF-8']
    
    def test_detect_encoding_empty(self):
        """Test encoding detection for empty content."""
        encoding = self.handler.detect_encoding(b"")
        assert encoding == self.config.default_encoding
    
    def test_validate_encoding_valid(self):
        """Test encoding validation with valid encoding."""
        content = "Hello, world!"
        assert self.handler.validate_encoding(content, 'utf-8')
    
    def test_validate_encoding_invalid(self):
        """Test encoding validation with invalid encoding."""
        content = "Hello, 世界!"
        assert not self.handler.validate_encoding(content, 'ascii')


class TestOutputFormatter:
    """Test cases for OutputFormatter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config()
        self.formatter = OutputFormatter(self.config)
    
    def test_format_plain_string(self):
        """Test formatting plain string."""
        result = self.formatter.format_output("hello world", OutputFormat.PLAIN)
        assert result == "hello world"
    
    def test_format_plain_none(self):
        """Test formatting None value."""
        result = self.formatter.format_output(None, OutputFormat.PLAIN)
        assert result == ""
    
    def test_format_json_dict(self):
        """Test formatting dictionary as JSON."""
        data = {"key": "value", "number": 42}
        result = self.formatter.format_output(data, OutputFormat.JSON)
        
        # Parse back to verify it's valid JSON
        parsed = json.loads(result)
        assert parsed == data
    
    def test_format_json_string(self):
        """Test formatting JSON string."""
        json_str = '{"key": "value"}'
        result = self.formatter.format_output(json_str, OutputFormat.JSON)
        
        # Should be pretty-printed
        assert "{\n" in result
        assert '"key": "value"' in result
    
    def test_format_auto_detection(self):
        """Test automatic format detection."""
        # Dictionary should be detected as JSON
        data = {"key": "value"}
        result = self.formatter.format_output(data, OutputFormat.AUTO)
        parsed = json.loads(result)
        assert parsed == data
        
        # Plain string should remain plain
        plain_data = "hello world"
        result = self.formatter.format_output(plain_data, OutputFormat.AUTO)
        assert result == plain_data
    
    def test_format_table_dict_list(self):
        """Test formatting list of dictionaries as table."""
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ]
        result = self.formatter.format_output(data, OutputFormat.TABLE)
        
        assert "name" in result
        assert "age" in result
        assert "Alice" in result
        assert "Bob" in result
        assert "|" in result  # Table separator
    
    def test_format_table_dict(self):
        """Test formatting dictionary as table."""
        data = {"key1": "value1", "key2": "value2"}
        result = self.formatter.format_output(data, OutputFormat.TABLE)
        
        assert "Key" in result
        assert "Value" in result
        assert "key1" in result
        assert "value1" in result
        assert "|" in result  # Table separator


class TestErrorHandler:
    """Test cases for ErrorHandler class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config()
        self.handler = ErrorHandler(self.config)
    
    def test_handle_file_not_found(self):
        """Test handling FileNotFoundError."""
        error = FileNotFoundError("File not found")
        result = self.handler.handle_file_error(error, "test.txt")
        
        assert not result.success
        assert "File not found" in result.error_message
        assert "test.txt" in result.error_message
        assert "suggestions" in result.metadata
        assert len(result.metadata["suggestions"]) > 0
    
    def test_handle_permission_error(self):
        """Test handling PermissionError."""
        error = PermissionError("Permission denied")
        result = self.handler.handle_file_error(error, "test.txt")
        
        assert not result.success
        assert "Permission denied" in result.error_message
        assert "test.txt" in result.error_message
        assert "suggestions" in result.metadata
    
    def test_handle_parsing_error_json(self):
        """Test handling JSON parsing error."""
        error = json.JSONDecodeError("Invalid JSON", "test", 10)
        result = self.handler.handle_parsing_error(error, "JSON", 10)
        
        assert not result.success
        assert "JSON" in result.error_message
        assert "position 10" in result.error_message
        assert "suggestions" in result.metadata
        assert any("JSON" in suggestion for suggestion in result.metadata["suggestions"])
    
    def test_handle_input_error_empty(self):
        """Test handling empty input error."""
        error = ValueError("Empty input")
        result = self.handler.handle_input_error(error, "stdin")
        
        assert not result.success
        assert "No input data provided" in result.error_message
        assert "stdin" in result.error_message
        assert "suggestions" in result.metadata
    
    def test_handle_generic_error(self):
        """Test handling generic error."""
        error = RuntimeError("Something went wrong")
        result = self.handler.handle_generic_error(error, "test operation")
        
        assert not result.success
        assert "test operation" in result.error_message
        assert "Something went wrong" in result.error_message
        assert "suggestions" in result.metadata