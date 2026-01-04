"""
Tests for core interfaces.
"""

import pytest
from devknife.core.interfaces import UtilityModule
from devknife.core.models import Command, InputData, ProcessingResult, InputSource


class MockUtilityModule(UtilityModule):
    """Mock implementation of UtilityModule for testing."""
    
    def process(self, input_data: InputData, options: dict) -> ProcessingResult:
        return ProcessingResult(success=True, output=f"Processed: {input_data.as_string()}")
    
    def get_help(self) -> str:
        return "Mock utility help text"
    
    def validate_input(self, input_data: InputData) -> bool:
        return len(input_data.as_string()) > 0
    
    def get_command_info(self) -> Command:
        return Command(
            name="mock",
            description="Mock utility for testing",
            category="test",
            module="tests.mock"
        )


class TestUtilityModule:
    """Tests for UtilityModule interface."""
    
    def test_mock_implementation(self):
        """Test that mock implementation works correctly."""
        util = MockUtilityModule()
        
        # Test process method
        input_data = InputData(content="test data", source=InputSource.ARGS)
        result = util.process(input_data, {})
        assert result.success is True
        assert result.output == "Processed: test data"
        
        # Test get_help method
        help_text = util.get_help()
        assert help_text == "Mock utility help text"
        
        # Test validate_input method
        assert util.validate_input(input_data) is True
        
        empty_data = InputData(content="", source=InputSource.ARGS)
        assert util.validate_input(empty_data) is False
        
        # Test get_command_info method
        cmd = util.get_command_info()
        assert cmd.name == "mock"
        assert cmd.description == "Mock utility for testing"
        assert cmd.category == "test"
        assert cmd.module == "tests.mock"
    
    def test_abstract_methods(self):
        """Test that UtilityModule cannot be instantiated directly."""
        with pytest.raises(TypeError):
            UtilityModule()
    
    def test_default_methods(self):
        """Test default implementations of optional methods."""
        util = MockUtilityModule()
        
        # Test get_supported_options default implementation
        options = util.get_supported_options()
        assert options == []
        
        # Test get_examples default implementation
        examples = util.get_examples()
        assert examples == []