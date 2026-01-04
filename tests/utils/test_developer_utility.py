"""
Tests for developer utility modules.
"""

import re
import uuid
import pytest
from devknife.core import InputData, InputSource
from devknife.utils.developer_utility import (
    UUIDGenerator,
    UUIDDecoder,
    IBANValidator,
    PasswordGenerator
)


class TestUUIDGenerator:
    """Test cases for UUID generator utility."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.utility = UUIDGenerator()
    
    def test_uuid_generation_default(self):
        """Test default UUID generation (version 4)."""
        input_data = InputData(content="", source=InputSource.ARGS)
        result = self.utility.process(input_data, {})
        
        assert result.success is True
        assert len(result.output) == 36  # Standard UUID format length
        assert result.metadata['operation'] == 'generate'
        assert result.metadata['version'] == 4
        
        # Validate UUID format
        uuid_pattern = re.compile(
            r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'
        )
        assert uuid_pattern.match(result.output) is not None
    
    def test_uuid_generation_version_1(self):
        """Test UUID version 1 generation."""
        input_data = InputData(content="", source=InputSource.ARGS)
        result = self.utility.process(input_data, {'version': 1})
        
        assert result.success is True
        assert len(result.output) == 36
        assert result.metadata['version'] == 1
        
        # Validate that it's a valid UUID
        try:
            parsed_uuid = uuid.UUID(result.output)
            assert parsed_uuid.version == 1
        except ValueError:
            pytest.fail("Generated UUID is not valid")
    
    def test_uuid_generation_version_4(self):
        """Test UUID version 4 generation."""
        input_data = InputData(content="", source=InputSource.ARGS)
        result = self.utility.process(input_data, {'version': 4})
        
        assert result.success is True
        assert len(result.output) == 36
        assert result.metadata['version'] == 4
        
        # Validate that it's a valid UUID
        try:
            parsed_uuid = uuid.UUID(result.output)
            assert parsed_uuid.version == 4
        except ValueError:
            pytest.fail("Generated UUID is not valid")
    
    def test_unsupported_uuid_version(self):
        """Test handling of unsupported UUID versions."""
        input_data = InputData(content="", source=InputSource.ARGS)
        result = self.utility.process(input_data, {'version': 3})
        
        assert result.success is False
        assert "Unsupported UUID version" in result.error_message
    
    def test_input_validation(self):
        """Test input validation (always valid for generation)."""
        input_data = InputData(content="anything", source=InputSource.ARGS)
        assert self.utility.validate_input(input_data) is True
        
        input_data = InputData(content="", source=InputSource.ARGS)
        assert self.utility.validate_input(input_data) is True
    
    def test_command_info(self):
        """Test command information."""
        command = self.utility.get_command_info()
        assert command.name == "uuid-gen"
        assert command.category == "developer"
        assert command.cli_enabled is True
        assert command.tui_enabled is True


class TestUUIDDecoder:
    """Test cases for UUID decoder utility."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.utility = UUIDDecoder()
    
    def test_uuid_decoding_version_4(self):
        """Test decoding of version 4 UUID."""
        test_uuid = "550e8400-e29b-41d4-a716-446655440000"
        input_data = InputData(content=test_uuid, source=InputSource.ARGS)
        result = self.utility.process(input_data, {})
        
        assert result.success is True
        assert test_uuid in result.output
        assert "Version: 4" in result.output
        assert result.metadata['operation'] == 'decode'
        assert result.metadata['uuid_version'] == 4
    
    def test_uuid_decoding_version_1(self):
        """Test decoding of version 1 UUID."""
        # Generate a version 1 UUID for testing
        test_uuid = str(uuid.uuid1())
        input_data = InputData(content=test_uuid, source=InputSource.ARGS)
        result = self.utility.process(input_data, {})
        
        assert result.success is True
        assert test_uuid in result.output
        assert "Version: 1" in result.output
        assert "Timestamp:" in result.output
        assert result.metadata['uuid_version'] == 1
    
    def test_invalid_uuid_format(self):
        """Test handling of invalid UUID format."""
        invalid_uuid = "not-a-uuid"
        input_data = InputData(content=invalid_uuid, source=InputSource.ARGS)
        result = self.utility.process(input_data, {})
        
        assert result.success is False
        assert "Invalid UUID format" in result.error_message
    
    def test_malformed_uuid(self):
        """Test handling of malformed UUID."""
        malformed_uuid = "550e8400-e29b-41d4-a716-44665544000"  # Missing one character
        input_data = InputData(content=malformed_uuid, source=InputSource.ARGS)
        result = self.utility.process(input_data, {})
        
        assert result.success is False
        assert "Invalid UUID format" in result.error_message
    
    def test_input_validation_valid(self):
        """Test input validation with valid UUID."""
        valid_uuid = "550e8400-e29b-41d4-a716-446655440000"
        input_data = InputData(content=valid_uuid, source=InputSource.ARGS)
        assert self.utility.validate_input(input_data) is True
    
    def test_input_validation_invalid(self):
        """Test input validation with invalid UUID."""
        invalid_uuid = "not-a-uuid"
        input_data = InputData(content=invalid_uuid, source=InputSource.ARGS)
        assert self.utility.validate_input(input_data) is False
    
    def test_command_info(self):
        """Test command information."""
        command = self.utility.get_command_info()
        assert command.name == "uuid-decode"
        assert command.category == "developer"
        assert command.cli_enabled is True
        assert command.tui_enabled is True


class TestIBANValidator:
    """Test cases for IBAN validator utility."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.utility = IBANValidator()
    
    def test_valid_iban_gb(self):
        """Test validation of valid GB IBAN."""
        valid_iban = "GB82WEST12345698765432"
        input_data = InputData(content=valid_iban, source=InputSource.ARGS)
        result = self.utility.process(input_data, {})
        
        assert result.success is True
        assert "Valid IBAN" in result.output
        assert result.metadata['valid'] is True
        assert result.metadata['country_code'] == "GB"
    
    def test_valid_iban_de(self):
        """Test validation of valid DE IBAN."""
        valid_iban = "DE89370400440532013000"
        input_data = InputData(content=valid_iban, source=InputSource.ARGS)
        result = self.utility.process(input_data, {})
        
        assert result.success is True
        assert "Valid IBAN" in result.output
        assert result.metadata['valid'] is True
        assert result.metadata['country_code'] == "DE"
    
    def test_invalid_iban_checksum(self):
        """Test validation of IBAN with invalid checksum."""
        invalid_iban = "GB82WEST12345698765433"  # Last digit changed
        input_data = InputData(content=invalid_iban, source=InputSource.ARGS)
        result = self.utility.process(input_data, {})
        
        assert result.success is True
        assert "Invalid IBAN checksum" in result.output
        assert result.metadata['valid'] is False
    
    def test_invalid_iban_format(self):
        """Test validation of invalid IBAN format."""
        invalid_iban = "INVALID"
        input_data = InputData(content=invalid_iban, source=InputSource.ARGS)
        result = self.utility.process(input_data, {})
        
        assert result.success is True
        assert "Invalid IBAN format" in result.output
        assert result.metadata['valid'] is False
    
    def test_invalid_iban_length(self):
        """Test validation of IBAN with incorrect length."""
        invalid_iban = "GB82WEST123456987654"  # Too short for GB
        input_data = InputData(content=invalid_iban, source=InputSource.ARGS)
        result = self.utility.process(input_data, {})
        
        assert result.success is True
        assert "Invalid IBAN length" in result.output
        assert result.metadata['valid'] is False
    
    def test_iban_with_spaces(self):
        """Test validation of IBAN with spaces."""
        iban_with_spaces = "GB82 WEST 1234 5698 7654 32"
        input_data = InputData(content=iban_with_spaces, source=InputSource.ARGS)
        result = self.utility.process(input_data, {})
        
        assert result.success is True
        assert "Valid IBAN" in result.output
        assert result.metadata['valid'] is True
    
    def test_input_validation_valid(self):
        """Test input validation with valid IBAN format."""
        valid_iban = "GB82WEST12345698765432"
        input_data = InputData(content=valid_iban, source=InputSource.ARGS)
        assert self.utility.validate_input(input_data) is True
    
    def test_input_validation_invalid(self):
        """Test input validation with invalid format."""
        invalid_iban = "INVALID"
        input_data = InputData(content=invalid_iban, source=InputSource.ARGS)
        assert self.utility.validate_input(input_data) is False
    
    def test_command_info(self):
        """Test command information."""
        command = self.utility.get_command_info()
        assert command.name == "iban"
        assert command.category == "developer"
        assert command.cli_enabled is True
        assert command.tui_enabled is True


class TestPasswordGenerator:
    """Test cases for password generator utility."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.utility = PasswordGenerator()
    
    def test_password_generation_default(self):
        """Test default password generation."""
        input_data = InputData(content="", source=InputSource.ARGS)
        result = self.utility.process(input_data, {})
        
        assert result.success is True
        assert len(result.output) == 16  # Default length
        assert result.metadata['operation'] == 'generate'
        assert result.metadata['length'] == 16
        
        # Check that password contains different character types
        password = result.output
        assert any(c.islower() for c in password)
        assert any(c.isupper() for c in password)
        assert any(c.isdigit() for c in password)
        assert any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
    
    def test_password_generation_custom_length(self):
        """Test password generation with custom length."""
        input_data = InputData(content="", source=InputSource.ARGS)
        result = self.utility.process(input_data, {'length': 32})
        
        assert result.success is True
        assert len(result.output) == 32
        assert result.metadata['length'] == 32
    
    def test_password_generation_no_symbols(self):
        """Test password generation without symbols."""
        input_data = InputData(content="", source=InputSource.ARGS)
        result = self.utility.process(input_data, {'symbols': False})
        
        assert result.success is True
        password = result.output
        
        # Should not contain symbols
        assert not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        # Should still contain other character types
        assert any(c.islower() for c in password)
        assert any(c.isupper() for c in password)
        assert any(c.isdigit() for c in password)
    
    def test_password_generation_no_ambiguous(self):
        """Test password generation without ambiguous characters."""
        input_data = InputData(content="", source=InputSource.ARGS)
        result = self.utility.process(input_data, {'no_ambiguous': True})
        
        assert result.success is True
        password = result.output
        
        # Should not contain ambiguous characters
        ambiguous_chars = "0O1lI|"
        assert not any(c in ambiguous_chars for c in password)
    
    def test_password_generation_minimum_length(self):
        """Test password generation with minimum length."""
        input_data = InputData(content="", source=InputSource.ARGS)
        result = self.utility.process(input_data, {'length': 4})
        
        assert result.success is True
        assert len(result.output) == 4
    
    def test_password_generation_too_short(self):
        """Test password generation with length too short."""
        input_data = InputData(content="", source=InputSource.ARGS)
        result = self.utility.process(input_data, {'length': 3})
        
        assert result.success is False
        assert "Password length must be at least 4" in result.error_message
    
    def test_password_generation_too_long(self):
        """Test password generation with length too long."""
        input_data = InputData(content="", source=InputSource.ARGS)
        result = self.utility.process(input_data, {'length': 300})
        
        assert result.success is False
        assert "Password length cannot exceed 256" in result.error_message
    
    def test_password_generation_no_character_types(self):
        """Test password generation with no character types enabled."""
        input_data = InputData(content="", source=InputSource.ARGS)
        result = self.utility.process(input_data, {
            'uppercase': False,
            'lowercase': False,
            'digits': False,
            'symbols': False
        })
        
        assert result.success is False
        assert "No character types selected" in result.error_message
    
    def test_password_strength_calculation(self):
        """Test password strength calculation."""
        input_data = InputData(content="", source=InputSource.ARGS)
        result = self.utility.process(input_data, {'length': 20})
        
        assert result.success is True
        assert 'strength_score' in result.metadata
        assert 'strength_level' in result.metadata
        assert isinstance(result.metadata['strength_score'], int)
        assert result.metadata['strength_score'] >= 0
        assert result.metadata['strength_score'] <= 100
    
    def test_input_validation(self):
        """Test input validation (always valid for generation)."""
        input_data = InputData(content="anything", source=InputSource.ARGS)
        assert self.utility.validate_input(input_data) is True
        
        input_data = InputData(content="", source=InputSource.ARGS)
        assert self.utility.validate_input(input_data) is True
    
    def test_command_info(self):
        """Test command information."""
        command = self.utility.get_command_info()
        assert command.name == "password"
        assert command.category == "developer"
        assert command.cli_enabled is True
        assert command.tui_enabled is True