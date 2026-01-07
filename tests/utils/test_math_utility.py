"""
Tests for mathematical transformation utilities.
"""

import pytest
from devknife.utils.math_utility import (
    NumberBaseConverter,
    HashGenerator,
    TimestampConverter,
)
from devknife.core.models import InputData, InputSource


class TestNumberBaseConverter:
    """Test cases for NumberBaseConverter utility."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = NumberBaseConverter()

    def test_decimal_to_all_bases(self):
        """Test converting decimal number to all bases."""
        input_data = InputData("255", InputSource.ARGS)
        result = self.converter.process(input_data, {})

        assert result.success
        assert "Decimal: 255" in result.output
        assert "Binary: 11111111" in result.output
        assert "Octal: 377" in result.output
        assert "Hexadecimal: FF" in result.output
        assert result.metadata["decimal_value"] == 255

    def test_binary_to_decimal(self):
        """Test converting binary to decimal."""
        input_data = InputData("1010", InputSource.ARGS)
        result = self.converter.process(input_data, {"to_base": "decimal"})

        assert result.success
        assert result.output == "10"
        assert result.metadata["decimal_value"] == 10
        assert result.metadata["input_base"] == "binary"

    def test_hex_with_prefix_to_binary(self):
        """Test converting hex with 0x prefix to binary."""
        input_data = InputData("0xFF", InputSource.ARGS)
        result = self.converter.process(input_data, {"to_base": "binary"})

        assert result.success
        assert result.output == "11111111"
        assert result.metadata["decimal_value"] == 255
        assert result.metadata["input_base"] == "hexadecimal"

    def test_octal_to_hex(self):
        """Test converting octal to hexadecimal."""
        input_data = InputData("0o777", InputSource.ARGS)
        result = self.converter.process(input_data, {"to_base": "hex"})

        assert result.success
        assert result.output == "1FF"
        assert result.metadata["decimal_value"] == 511
        assert result.metadata["input_base"] == "octal"

    def test_auto_detection_binary(self):
        """Test auto-detection of binary numbers."""
        input_data = InputData("101010", InputSource.ARGS)
        result = self.converter.process(input_data, {"to_base": "decimal"})

        assert result.success
        assert result.output == "42"
        assert result.metadata["input_base"] == "binary"

    def test_auto_detection_hex(self):
        """Test auto-detection of hexadecimal numbers."""
        input_data = InputData("DEADBEEF", InputSource.ARGS)
        result = self.converter.process(input_data, {"to_base": "decimal"})

        assert result.success
        assert result.output == "3735928559"
        assert result.metadata["input_base"] == "hexadecimal"

    def test_invalid_number_format(self):
        """Test handling of invalid number format."""
        input_data = InputData("invalid", InputSource.ARGS)
        result = self.converter.process(input_data, {})

        assert not result.success
        assert "Invalid number format" in result.error_message

    def test_empty_input(self):
        """Test handling of empty input."""
        input_data = InputData("", InputSource.ARGS)
        result = self.converter.process(input_data, {})

        assert not result.success
        assert "Empty input provided" in result.error_message

    def test_invalid_target_base(self):
        """Test handling of invalid target base."""
        input_data = InputData("255", InputSource.ARGS)
        result = self.converter.process(input_data, {"to_base": "invalid"})

        assert not result.success
        assert "Invalid target base" in result.error_message

    def test_input_validation_valid(self):
        """Test input validation with valid number."""
        input_data = InputData("123", InputSource.ARGS)
        assert self.converter.validate_input(input_data)

    def test_input_validation_invalid(self):
        """Test input validation with invalid input."""
        input_data = InputData("not_a_number", InputSource.ARGS)
        assert not self.converter.validate_input(input_data)

    def test_command_info(self):
        """Test command information."""
        command = self.converter.get_command_info()
        assert command.name == "base"
        assert command.category == "math"
        assert command.cli_enabled
        assert command.tui_enabled


class TestHashGenerator:
    """Test cases for HashGenerator utility."""

    def setup_method(self):
        """Set up test fixtures."""
        self.hasher = HashGenerator()

    def test_generate_all_hashes(self):
        """Test generating all hash types."""
        input_data = InputData("Hello, World!", InputSource.ARGS)
        result = self.hasher.process(input_data, {})

        assert result.success
        assert "MD5:" in result.output
        assert "SHA1:" in result.output
        assert "SHA256:" in result.output

        # Verify known hash values
        hashes = result.metadata["hashes"]
        assert hashes["md5"] == "65a8e27d8879283831b664bd8b7f0ad4"
        assert hashes["sha1"] == "0a0a9f2a6772942557ab5355d76af442f8f65e01"
        assert (
            hashes["sha256"]
            == "dffd6021bb2bd5b0af676290809ec3a53191dd81c7f70a4b28688a362182986f"
        )

    def test_generate_md5_only(self):
        """Test generating MD5 hash only."""
        input_data = InputData("test", InputSource.ARGS)
        result = self.hasher.process(input_data, {"algorithm": "md5"})

        assert result.success
        assert result.output == "098f6bcd4621d373cade4e832627b4f6"
        assert result.metadata["algorithm"] == "md5"

    def test_generate_sha1_only(self):
        """Test generating SHA1 hash only."""
        input_data = InputData("test", InputSource.ARGS)
        result = self.hasher.process(input_data, {"algorithm": "sha1"})

        assert result.success
        assert result.output == "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3"
        assert result.metadata["algorithm"] == "sha1"

    def test_generate_sha256_only(self):
        """Test generating SHA256 hash only."""
        input_data = InputData("test", InputSource.ARGS)
        result = self.hasher.process(input_data, {"algorithm": "sha256"})

        assert result.success
        assert (
            result.output
            == "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
        )
        assert result.metadata["algorithm"] == "sha256"

    def test_invalid_algorithm(self):
        """Test handling of invalid hash algorithm."""
        input_data = InputData("test", InputSource.ARGS)
        result = self.hasher.process(input_data, {"algorithm": "invalid"})

        assert not result.success
        assert "Invalid hash algorithm" in result.error_message

    def test_empty_string_hash(self):
        """Test hashing empty string."""
        input_data = InputData("", InputSource.ARGS)
        result = self.hasher.process(input_data, {"algorithm": "md5"})

        assert result.success
        assert (
            result.output == "d41d8cd98f00b204e9800998ecf8427e"
        )  # MD5 of empty string

    def test_unicode_string_hash(self):
        """Test hashing Unicode string."""
        input_data = InputData("Hello, 世界!", InputSource.ARGS)
        result = self.hasher.process(input_data, {"algorithm": "sha256"})

        assert result.success
        # Should handle UTF-8 encoding properly
        assert len(result.output) == 64  # SHA256 hex length

    def test_input_validation(self):
        """Test input validation (always valid for hashing)."""
        input_data = InputData("any string", InputSource.ARGS)
        assert self.hasher.validate_input(input_data)

        input_data = InputData("", InputSource.ARGS)
        assert self.hasher.validate_input(input_data)

    def test_command_info(self):
        """Test command information."""
        command = self.hasher.get_command_info()
        assert command.name == "hash"
        assert command.category == "math"
        assert command.cli_enabled
        assert command.tui_enabled


class TestTimestampConverter:
    """Test cases for TimestampConverter utility."""

    def setup_method(self):
        """Set up test fixtures."""
        self.converter = TimestampConverter()

    def test_unix_timestamp_to_date(self):
        """Test converting Unix timestamp to human-readable date."""
        input_data = InputData(
            "1640995200", InputSource.ARGS
        )  # 2022-01-01 09:00:00 UTC
        result = self.converter.process(input_data, {"utc": True})

        assert result.success
        assert "Unix Timestamp: 1640995200" in result.output
        assert "2022-01-01" in result.output
        assert result.metadata["input_timestamp"] == 1640995200

    def test_float_timestamp_to_date(self):
        """Test converting float Unix timestamp to date."""
        input_data = InputData("1640995200.5", InputSource.ARGS)
        result = self.converter.process(input_data, {"utc": True})

        assert result.success
        assert "Unix Timestamp: 1640995200.5" in result.output
        assert "2022-01-01" in result.output

    def test_millisecond_timestamp_to_date(self):
        """Test converting millisecond timestamp to date."""
        input_data = InputData("1640995200000", InputSource.ARGS)  # Milliseconds
        result = self.converter.process(input_data, {"utc": True})

        assert result.success
        assert "2022-01-01" in result.output
        # Should automatically detect and convert from milliseconds

    def test_date_to_timestamp_iso_format(self):
        """Test converting ISO date to Unix timestamp."""
        input_data = InputData("2022-01-01 00:00:00", InputSource.ARGS)
        result = self.converter.process(input_data, {"reverse": True})

        assert result.success
        assert "Unix Timestamp:" in result.output
        assert "2022-01-01" in result.output
        assert result.metadata["operation"] == "date_to_timestamp"

    def test_date_to_timestamp_simple_format(self):
        """Test converting simple date to Unix timestamp."""
        input_data = InputData("2022-01-01", InputSource.ARGS)
        result = self.converter.process(input_data, {"reverse": True})

        assert result.success
        assert "Unix Timestamp:" in result.output
        assert "2022-01-01" in result.output

    def test_readable_format_output(self):
        """Test readable format output."""
        input_data = InputData("1640995200", InputSource.ARGS)
        result = self.converter.process(input_data, {"format": "readable", "utc": True})

        assert result.success
        assert "2022-01-01" in result.output
        assert "Timezone: UTC" in result.output

    def test_invalid_timestamp(self):
        """Test handling of invalid timestamp."""
        input_data = InputData("invalid_timestamp", InputSource.ARGS)
        result = self.converter.process(input_data, {})

        assert not result.success
        assert "Invalid timestamp format" in result.error_message

    def test_invalid_date_format(self):
        """Test handling of invalid date format."""
        input_data = InputData("invalid date", InputSource.ARGS)
        result = self.converter.process(input_data, {"reverse": True})

        assert not result.success
        assert "Could not parse date format" in result.error_message

    def test_empty_input(self):
        """Test handling of empty input."""
        input_data = InputData("", InputSource.ARGS)
        result = self.converter.process(input_data, {})

        assert not result.success
        assert "Empty input provided" in result.error_message

    def test_input_validation_valid_timestamp(self):
        """Test input validation with valid timestamp."""
        input_data = InputData("1640995200", InputSource.ARGS)
        assert self.converter.validate_input(input_data)

    def test_input_validation_valid_date(self):
        """Test input validation with valid date."""
        input_data = InputData("2022-01-01", InputSource.ARGS)
        assert self.converter.validate_input(input_data)

    def test_input_validation_invalid(self):
        """Test input validation with invalid input."""
        input_data = InputData("not_a_date_or_timestamp", InputSource.ARGS)
        assert not self.converter.validate_input(input_data)

    def test_command_info(self):
        """Test command information."""
        command = self.converter.get_command_info()
        assert command.name == "timestamp"
        assert command.category == "math"
        assert command.cli_enabled
        assert command.tui_enabled
