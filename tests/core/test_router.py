"""
Tests for the command router and registry system.
"""

import pytest
from typing import Any, Dict, List

from devknife.core import (
    CommandRegistry, 
    CommandRouter, 
    UtilityModule, 
    Command, 
    InputData, 
    ProcessingResult,
    InputSource
)
from devknife.utils import ExampleUtility


class MockUtility(UtilityModule):
    """Mock utility for testing purposes."""
    
    def process(self, input_data: InputData, options: Dict[str, Any]) -> ProcessingResult:
        return ProcessingResult(
            success=True,
            output=f"Processed: {input_data.as_string()}",
            metadata={'test': True}
        )
    
    def get_help(self) -> str:
        return "Mock utility help text"
    
    def validate_input(self, input_data: InputData) -> bool:
        return len(input_data.as_string().strip()) > 0
    
    def get_command_info(self) -> Command:
        return Command(
            name="mock",
            description="Mock utility for testing",
            category="test",
            module="test_module"
        )
    
    def get_supported_options(self) -> List[str]:
        return ["option1", "option2"]
    
    def get_examples(self) -> List[str]:
        return ["mock example1", "mock example2"]


class TestCommandRegistry:
    """Test cases for CommandRegistry."""
    
    def test_register_utility(self):
        """Test registering a utility module."""
        registry = CommandRegistry()
        
        # Register a utility
        registry.register_utility(MockUtility)
        
        # Check it was registered
        assert "mock" in registry._utilities
        assert "mock" in registry._commands
        assert "test" in registry._categories
        assert "mock" in registry._categories["test"]
    
    def test_register_duplicate_utility(self):
        """Test registering a duplicate utility raises error."""
        registry = CommandRegistry()
        
        # Register utility twice
        registry.register_utility(MockUtility)
        
        with pytest.raises(ValueError, match="already registered"):
            registry.register_utility(MockUtility)
    
    def test_register_invalid_utility(self):
        """Test registering invalid utility raises error."""
        registry = CommandRegistry()
        
        class InvalidUtility:
            pass
        
        with pytest.raises(ValueError, match="must inherit from UtilityModule"):
            registry.register_utility(InvalidUtility)
    
    def test_unregister_utility(self):
        """Test unregistering a utility module."""
        registry = CommandRegistry()
        
        # Register and then unregister
        registry.register_utility(MockUtility)
        assert "mock" in registry._utilities
        
        registry.unregister_utility("mock")
        assert "mock" not in registry._utilities
        assert "mock" not in registry._commands
    
    def test_get_utility_class(self):
        """Test getting utility class by command name."""
        registry = CommandRegistry()
        registry.register_utility(MockUtility)
        
        # Get existing utility
        utility_class = registry.get_utility_class("mock")
        assert utility_class == MockUtility
        
        # Get non-existing utility
        utility_class = registry.get_utility_class("nonexistent")
        assert utility_class is None
    
    def test_get_command_info(self):
        """Test getting command information."""
        registry = CommandRegistry()
        registry.register_utility(MockUtility)
        
        # Get existing command info
        command_info = registry.get_command_info("mock")
        assert command_info is not None
        assert command_info.name == "mock"
        assert command_info.description == "Mock utility for testing"
        
        # Get non-existing command info
        command_info = registry.get_command_info("nonexistent")
        assert command_info is None
    
    def test_list_commands(self):
        """Test listing commands with various filters."""
        registry = CommandRegistry()
        registry.register_utility(MockUtility)
        registry.register_utility(ExampleUtility)
        
        # List all commands
        commands = registry.list_commands()
        assert "mock" in commands
        assert "echo" in commands
        
        # List by category
        test_commands = registry.list_commands(category="test")
        assert "mock" in test_commands
        assert "echo" not in test_commands
        
        example_commands = registry.list_commands(category="example")
        assert "echo" in example_commands
        assert "mock" not in example_commands
    
    def test_list_categories(self):
        """Test listing categories."""
        registry = CommandRegistry()
        registry.register_utility(MockUtility)
        registry.register_utility(ExampleUtility)
        
        categories = registry.list_categories()
        assert "test" in categories
        assert "example" in categories
    
    def test_get_commands_by_category(self):
        """Test getting commands by category."""
        registry = CommandRegistry()
        registry.register_utility(MockUtility)
        registry.register_utility(ExampleUtility)
        
        test_commands = registry.get_commands_by_category("test")
        assert "mock" in test_commands
        
        example_commands = registry.get_commands_by_category("example")
        assert "echo" in example_commands
        
        # Non-existing category
        nonexistent_commands = registry.get_commands_by_category("nonexistent")
        assert len(nonexistent_commands) == 0


class TestCommandRouter:
    """Test cases for CommandRouter."""
    
    def test_route_command_success(self):
        """Test successful command routing."""
        registry = CommandRegistry()
        registry.register_utility(MockUtility)
        router = CommandRouter(registry)
        
        input_data = InputData("test input", InputSource.ARGS)
        result = router.route_command("mock", input_data)
        
        assert result.success is True
        assert "Processed: test input" in result.output
        assert result.metadata.get('test') is True
    
    def test_route_command_invalid_command(self):
        """Test routing invalid command."""
        registry = CommandRegistry()
        router = CommandRouter(registry)
        
        input_data = InputData("test input", InputSource.ARGS)
        result = router.route_command("nonexistent", input_data)
        
        assert result.success is False
        assert "Unknown command" in result.error_message
    
    def test_route_command_invalid_input(self):
        """Test routing with invalid input."""
        registry = CommandRegistry()
        registry.register_utility(MockUtility)
        router = CommandRouter(registry)
        
        # Empty input should be invalid for MockUtility
        input_data = InputData("", InputSource.ARGS)
        result = router.route_command("mock", input_data)
        
        assert result.success is False
        assert "Invalid input" in result.error_message
    
    def test_is_valid_command(self):
        """Test command validation."""
        registry = CommandRegistry()
        registry.register_utility(MockUtility)
        router = CommandRouter(registry)
        
        assert router.is_valid_command("mock") is True
        assert router.is_valid_command("nonexistent") is False
    
    def test_get_command_help(self):
        """Test getting command help."""
        registry = CommandRegistry()
        registry.register_utility(MockUtility)
        router = CommandRouter(registry)
        
        # Get help for existing command
        help_text = router.get_command_help("mock")
        assert help_text == "Mock utility help text"
        
        # Get help for non-existing command
        help_text = router.get_command_help("nonexistent")
        assert help_text is None
    
    def test_get_general_help(self):
        """Test getting general help."""
        registry = CommandRegistry()
        registry.register_utility(MockUtility)
        registry.register_utility(ExampleUtility)
        router = CommandRouter(registry)
        
        help_text = router.get_general_help()
        
        assert "DevKnife - Developer Utility Toolkit" in help_text
        assert "mock" in help_text
        assert "echo" in help_text
        assert "TEST:" in help_text
        assert "EXAMPLE:" in help_text
    
    def test_validate_command_options(self):
        """Test command option validation."""
        registry = CommandRegistry()
        registry.register_utility(MockUtility)
        router = CommandRouter(registry)
        
        # Valid options
        result = router.validate_command_options("mock", {"option1": "value1"})
        assert result.success is True
        
        # Invalid options
        result = router.validate_command_options("mock", {"invalid_option": "value"})
        assert result.success is False
        assert "Unsupported options" in result.error_message
        
        # Non-existing command
        result = router.validate_command_options("nonexistent", {})
        assert result.success is False
        assert "Unknown command" in result.error_message
    
    def test_get_command_examples(self):
        """Test getting command examples."""
        registry = CommandRegistry()
        registry.register_utility(MockUtility)
        router = CommandRouter(registry)
        
        # Get examples for existing command
        examples = router.get_command_examples("mock")
        assert "mock example1" in examples
        assert "mock example2" in examples
        
        # Get examples for non-existing command
        examples = router.get_command_examples("nonexistent")
        assert len(examples) == 0
    
    def test_clear_cache(self):
        """Test clearing utility instance cache."""
        registry = CommandRegistry()
        registry.register_utility(MockUtility)
        router = CommandRouter(registry)
        
        # Create an instance by routing a command
        input_data = InputData("test", InputSource.ARGS)
        router.route_command("mock", input_data)
        
        # Check instance is cached
        assert "mock" in router._utility_instances
        
        # Clear cache
        router.clear_cache()
        assert len(router._utility_instances) == 0


def test_global_registry_and_router():
    """Test global registry and router functions."""
    from devknife.core import get_global_registry, get_global_router, register_utility
    
    # Get global instances
    registry = get_global_registry()
    router = get_global_router()
    
    assert isinstance(registry, CommandRegistry)
    assert isinstance(router, CommandRouter)
    
    # Register utility using global function
    register_utility(MockUtility)
    
    # Check it was registered in global registry
    assert router.is_valid_command("mock")