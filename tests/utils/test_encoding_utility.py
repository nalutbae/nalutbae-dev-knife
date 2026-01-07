"""
Tests for encoding utility modules.
"""

import pytest
from devknife.core import InputData, InputSource
from devknife.utils.encoding_utility import Base64EncoderDecoder, URLEncoderDecoder


class TestBase64EncoderDecoder:
    """Test cases for Base64 encoder/decoder utility."""

    def setup_method(self):
        """Set up test fixtures."""
        self.utility = Base64EncoderDecoder()

    def test_base64_encoding(self):
        """Test basic Base64 encoding functionality."""
        input_data = InputData(content="Hello World", source=InputSource.ARGS)
        result = self.utility.process(input_data, {})

        assert result.success is True
        assert result.output == "SGVsbG8gV29ybGQ="
        assert result.metadata["operation"] == "encode"

    def test_base64_decoding(self):
        """Test basic Base64 decoding functionality."""
        input_data = InputData(content="SGVsbG8gV29ybGQ=", source=InputSource.ARGS)
        result = self.utility.process(input_data, {"decode": True})

        assert result.success is True
        assert result.output == "Hello World"
        assert result.metadata["operation"] == "decode"

    def test_base64_round_trip(self):
        """Test Base64 encoding and decoding round trip."""
        original_text = "Hello World! This is a test."

        # Encode
        input_data = InputData(content=original_text, source=InputSource.ARGS)
        encode_result = self.utility.process(input_data, {})
        assert encode_result.success is True

        # Decode
        decode_input = InputData(content=encode_result.output, source=InputSource.ARGS)
        decode_result = self.utility.process(decode_input, {"decode": True})
        assert decode_result.success is True
        assert decode_result.output == original_text

    def test_invalid_base64_decoding(self):
        """Test handling of invalid Base64 strings."""
        invalid_base64 = "This is not base64!"
        input_data = InputData(content=invalid_base64, source=InputSource.ARGS)
        result = self.utility.process(input_data, {"decode": True})

        assert result.success is False
        assert "Invalid Base64 format" in result.error_message

    def test_empty_input_validation(self):
        """Test validation of empty input."""
        input_data = InputData(content="", source=InputSource.ARGS)
        assert self.utility.validate_input(input_data) is False

        input_data = InputData(content="   ", source=InputSource.ARGS)
        assert self.utility.validate_input(input_data) is False

    def test_valid_input_validation(self):
        """Test validation of valid input."""
        input_data = InputData(content="Hello World", source=InputSource.ARGS)
        assert self.utility.validate_input(input_data) is True

    def test_command_info(self):
        """Test command information."""
        command = self.utility.get_command_info()
        assert command.name == "base64"
        assert command.category == "encoding"
        assert command.cli_enabled is True
        assert command.tui_enabled is True


class TestURLEncoderDecoder:
    """Test cases for URL encoder/decoder utility."""

    def setup_method(self):
        """Set up test fixtures."""
        self.utility = URLEncoderDecoder()

    def test_url_encoding(self):
        """Test basic URL encoding functionality."""
        input_data = InputData(content="Hello World!", source=InputSource.ARGS)
        result = self.utility.process(input_data, {})

        assert result.success is True
        assert result.output == "Hello%20World%21"
        assert result.metadata["operation"] == "encode"

    def test_url_decoding(self):
        """Test basic URL decoding functionality."""
        input_data = InputData(content="Hello%20World%21", source=InputSource.ARGS)
        result = self.utility.process(input_data, {"decode": True})

        assert result.success is True
        assert result.output == "Hello World!"
        assert result.metadata["operation"] == "decode"

    def test_url_round_trip(self):
        """Test URL encoding and decoding round trip."""
        original_text = "Hello World! This is a test with special chars: @#$%^&*()"

        # Encode
        input_data = InputData(content=original_text, source=InputSource.ARGS)
        encode_result = self.utility.process(input_data, {})
        assert encode_result.success is True

        # Decode
        decode_input = InputData(content=encode_result.output, source=InputSource.ARGS)
        decode_result = self.utility.process(decode_input, {"decode": True})
        assert decode_result.success is True
        assert decode_result.output == original_text

    def test_url_safe_characters(self):
        """Test that URL encoding produces only safe characters."""
        input_data = InputData(content="Hello World! @#$%", source=InputSource.ARGS)
        result = self.utility.process(input_data, {})

        assert result.success is True
        # Check that result contains only URL-safe characters
        import re

        url_safe_pattern = re.compile(r"^[A-Za-z0-9\-_.~%]*$")
        assert url_safe_pattern.match(result.output) is not None

    def test_empty_input_validation(self):
        """Test validation of empty input."""
        input_data = InputData(content="", source=InputSource.ARGS)
        assert self.utility.validate_input(input_data) is False

        input_data = InputData(content="   ", source=InputSource.ARGS)
        assert self.utility.validate_input(input_data) is False

    def test_valid_input_validation(self):
        """Test validation of valid input."""
        input_data = InputData(content="Hello World!", source=InputSource.ARGS)
        assert self.utility.validate_input(input_data) is True

    def test_command_info(self):
        """Test command information."""
        command = self.utility.get_command_info()
        assert command.name == "url"
        assert command.category == "encoding"
        assert command.cli_enabled is True
        assert command.tui_enabled is True
