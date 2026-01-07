"""
Property-based tests for CLI command processing.

**Feature: python-devtui-toolkit, Property 21: CLI command processing**
**Validates: Requirements 6.2**
"""

import pytest
from hypothesis import given, strategies as st, assume
from typing import Dict, Any

from devknife.core import (
    CommandRouter,
    CommandRegistry,
    UtilityModule,
    Command,
    InputData,
    ProcessingResult,
    InputSource,
)


class MockUtilityForProperty(UtilityModule):
    """Mock utility for property-based testing."""

    def __init__(self, command_name: str = "test", category: str = "test"):
        self.command_name = command_name
        self.category = category

    def process(
        self, input_data: InputData, options: Dict[str, Any]
    ) -> ProcessingResult:
        """Process input data and return a successful result."""
        content = input_data.as_string()

        # Simulate processing by returning the input with some metadata
        return ProcessingResult(
            success=True,
            output=f"Processed: {content}",
            metadata={
                "input_length": len(content),
                "source": input_data.source.value,
                "options_count": len(options),
            },
        )

    def get_help(self) -> str:
        """Get help text."""
        return f"Help for {self.command_name} utility"

    def validate_input(self, input_data: InputData) -> bool:
        """Validate input - accept any non-empty string."""
        try:
            content = input_data.as_string().strip()
            return len(content) > 0
        except Exception:
            return False

    def get_command_info(self) -> Command:
        """Get command information."""
        return Command(
            name=self.command_name,
            description=f"Test utility for {self.command_name}",
            category=self.category,
            module="test_module",
            cli_enabled=True,
            tui_enabled=True,
        )

    def get_supported_options(self) -> list[str]:
        """Get supported options."""
        return ["option1", "option2", "verbose"]

    def get_examples(self) -> list[str]:
        """Get usage examples."""
        return [f"{self.command_name} example"]


class TestCLICommandProcessingProperty:
    """Property-based tests for CLI command processing."""

    def setup_method(self):
        """Set up test environment for each test method."""
        self.registry = CommandRegistry()
        self.router = CommandRouter(self.registry)

        # Register some test utilities
        self.registry.register_utility(MockUtilityForProperty)

        # Create additional test utilities with different names
        class MockUtility2(MockUtilityForProperty):
            def __init__(self):
                super().__init__("test2", "test")

        class MockUtility3(MockUtilityForProperty):
            def __init__(self):
                super().__init__("test3", "utilities")

        self.registry.register_utility(MockUtility2)
        self.registry.register_utility(MockUtility3)

    @given(
        command_name=st.sampled_from(["test", "test2", "test3"]),
        input_content=st.text(min_size=1, max_size=1000).filter(lambda x: x.strip()),
        input_source=st.sampled_from(
            [InputSource.ARGS, InputSource.STDIN, InputSource.FILE]
        ),
        options=st.dictionaries(
            st.sampled_from(["option1", "option2", "verbose"]),
            st.one_of(st.text(max_size=100), st.integers(), st.booleans()),
            max_size=3,
        ),
    )
    def test_cli_command_processing_property(
        self,
        command_name: str,
        input_content: str,
        input_source: InputSource,
        options: Dict[str, Any],
    ):
        """
        **Feature: python-devtui-toolkit, Property 21: CLI command processing**
        **Validates: Requirements 6.2**

        Property: For any valid command with arguments, CLI mode should process
        and return appropriate results.

        This test verifies that:
        1. Valid commands are processed successfully
        2. Results contain expected output
        3. Processing preserves input data integrity
        4. Options are handled correctly
        """
        # Arrange
        input_data = InputData(input_content, input_source)

        # Act
        result = self.router.route_command(command_name, input_data, options)

        # Assert - Property verification
        assert (
            result.success is True
        ), f"Command {command_name} should succeed for valid input"
        assert result.output is not None, "Successful processing should produce output"
        assert (
            result.error_message is None
        ), "Successful processing should not have error message"

        # Verify output contains processed input
        assert isinstance(result.output, str), "Output should be a string"
        assert (
            "Processed:" in result.output
        ), "Output should indicate processing occurred"
        assert (
            input_content in result.output
        ), "Output should contain original input content"

        # Verify metadata is populated correctly
        assert "input_length" in result.metadata, "Metadata should contain input length"
        assert result.metadata["input_length"] == len(
            input_content
        ), "Input length should be preserved"
        assert (
            result.metadata["source"] == input_source.value
        ), "Input source should be preserved"
        assert result.metadata["options_count"] == len(
            options
        ), "Options count should be preserved"

    @given(
        invalid_command=st.text(min_size=1, max_size=50).filter(
            lambda x: x not in ["test", "test2", "test3"] and x.strip()
        ),
        input_content=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
        input_source=st.sampled_from(
            [InputSource.ARGS, InputSource.STDIN, InputSource.FILE]
        ),
    )
    def test_invalid_command_handling_property(
        self, invalid_command: str, input_content: str, input_source: InputSource
    ):
        """
        Property: For any invalid command, the system should return appropriate error results.

        This test verifies that:
        1. Invalid commands are handled gracefully
        2. Error messages are informative
        3. System doesn't crash on invalid commands
        """
        # Arrange
        input_data = InputData(input_content, input_source)

        # Act
        result = self.router.route_command(invalid_command, input_data)

        # Assert - Property verification
        assert result.success is False, "Invalid commands should fail"
        assert result.output is None, "Failed processing should not produce output"
        assert (
            result.error_message is not None
        ), "Failed processing should have error message"
        assert (
            "Unknown command" in result.error_message
        ), "Error should indicate unknown command"
        assert (
            invalid_command in result.error_message
        ), "Error should mention the invalid command"

    @given(
        command_name=st.sampled_from(["test", "test2", "test3"]),
        input_source=st.sampled_from(
            [InputSource.ARGS, InputSource.STDIN, InputSource.FILE]
        ),
    )
    def test_empty_input_handling_property(
        self, command_name: str, input_source: InputSource
    ):
        """
        Property: For any command with empty/invalid input, the system should handle it appropriately.

        This test verifies that:
        1. Empty input is validated correctly
        2. Appropriate error messages are returned
        3. System handles validation failures gracefully
        """
        # Arrange - Create empty or whitespace-only input
        empty_inputs = ["", "   ", "\t", "\n", "  \n  \t  "]

        for empty_content in empty_inputs:
            input_data = InputData(empty_content, input_source)

            # Act
            result = self.router.route_command(command_name, input_data)

            # Assert - Property verification
            assert (
                result.success is False
            ), f"Empty input '{repr(empty_content)}' should fail validation"
            assert result.output is None, "Failed validation should not produce output"
            assert (
                result.error_message is not None
            ), "Failed validation should have error message"
            assert (
                "Invalid input" in result.error_message
            ), "Error should indicate invalid input"

    @given(
        command_name=st.sampled_from(["test", "test2", "test3"]),
        input_content=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
        invalid_options=st.dictionaries(
            st.text(min_size=1, max_size=20).filter(
                lambda x: x not in ["option1", "option2", "verbose"] and x.strip()
            ),
            st.text(max_size=50),
            min_size=1,
            max_size=3,
        ),
    )
    def test_invalid_options_handling_property(
        self, command_name: str, input_content: str, invalid_options: Dict[str, Any]
    ):
        """
        Property: For any command with invalid options, the system should validate and reject them.

        This test verifies that:
        1. Invalid options are detected
        2. Appropriate error messages are returned
        3. Option validation works correctly
        """
        # Arrange
        input_data = InputData(input_content, InputSource.ARGS)

        # Act
        validation_result = self.router.validate_command_options(
            command_name, invalid_options
        )

        # Assert - Property verification
        assert (
            validation_result.success is False
        ), "Invalid options should fail validation"
        assert (
            validation_result.error_message is not None
        ), "Failed validation should have error message"
        assert (
            "Unsupported options" in validation_result.error_message
        ), "Error should indicate unsupported options"

        # Verify that at least one invalid option is mentioned in the error
        invalid_option_names = list(invalid_options.keys())
        error_mentions_invalid_option = any(
            option_name in validation_result.error_message
            for option_name in invalid_option_names
        )
        assert (
            error_mentions_invalid_option
        ), "Error should mention at least one invalid option"

    @given(
        command_name=st.sampled_from(["test", "test2", "test3"]),
        input_content=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
        valid_options=st.dictionaries(
            st.sampled_from(["option1", "option2", "verbose"]),
            st.one_of(st.text(max_size=50), st.integers(), st.booleans()),
            max_size=3,
        ),
    )
    def test_valid_options_handling_property(
        self, command_name: str, input_content: str, valid_options: Dict[str, Any]
    ):
        """
        Property: For any command with valid options, the system should accept and process them.

        This test verifies that:
        1. Valid options are accepted
        2. Options are passed to the utility correctly
        3. Processing succeeds with valid options
        """
        # Arrange
        input_data = InputData(input_content, InputSource.ARGS)

        # Act
        validation_result = self.router.validate_command_options(
            command_name, valid_options
        )
        processing_result = self.router.route_command(
            command_name, input_data, valid_options
        )

        # Assert - Property verification
        assert validation_result.success is True, "Valid options should pass validation"
        assert (
            validation_result.error_message is None
        ), "Successful validation should not have error"

        assert (
            processing_result.success is True
        ), "Processing with valid options should succeed"
        assert (
            processing_result.output is not None
        ), "Successful processing should produce output"
        assert processing_result.metadata["options_count"] == len(
            valid_options
        ), "Options should be passed correctly"

    def test_command_help_property(self):
        """
        Property: For any registered command, help should be available and informative.

        This test verifies that:
        1. Help is available for all registered commands
        2. Help text is non-empty and informative
        3. Help system works consistently
        """
        # Get all registered commands
        commands = self.registry.list_commands()

        for command_name in commands:
            # Act
            help_text = self.router.get_command_help(command_name)

            # Assert - Property verification
            assert (
                help_text is not None
            ), f"Help should be available for command '{command_name}'"
            assert isinstance(help_text, str), "Help text should be a string"
            assert (
                len(help_text.strip()) > 0
            ), f"Help text should not be empty for command '{command_name}'"
            assert (
                command_name in help_text or "Help for" in help_text
            ), "Help should reference the command"

    def test_general_help_property(self):
        """
        Property: General help should always be available and contain all registered commands.

        This test verifies that:
        1. General help is always available
        2. All registered commands are mentioned
        3. Help format is consistent and informative
        """
        # Act
        general_help = self.router.get_general_help()

        # Assert - Property verification
        assert general_help is not None, "General help should always be available"
        assert isinstance(general_help, str), "General help should be a string"
        assert len(general_help.strip()) > 0, "General help should not be empty"
        assert "DevKnife" in general_help, "General help should mention DevKnife"

        # Verify all registered commands are mentioned
        commands = self.registry.list_commands()
        for command_name in commands:
            assert (
                command_name in general_help
            ), f"General help should mention command '{command_name}'"
