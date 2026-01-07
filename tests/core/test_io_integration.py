"""
Integration tests for input/output processing with core models.
"""

import tempfile
import json
from pathlib import Path
from io import StringIO

from devknife.core import (
    InputHandler,
    OutputFormatter,
    ErrorHandler,
    InputData,
    InputSource,
    ProcessingResult,
    Config,
)


class TestIOIntegration:
    """Integration tests for I/O components with core models."""

    def setup_method(self):
        """Set up test fixtures."""
        self.config = Config()
        self.input_handler = InputHandler(self.config)
        self.output_formatter = OutputFormatter(self.config)
        self.error_handler = ErrorHandler(self.config)

    def test_complete_workflow_args_to_json(self):
        """Test complete workflow from args input to JSON output."""
        # Step 1: Read from args
        args = ["hello", "world"]
        input_data = self.input_handler.read_from_args(args)

        # Verify input data structure
        assert isinstance(input_data, InputData)
        assert input_data.source == InputSource.ARGS
        assert input_data.content == "hello world"

        # Step 2: Create a processing result
        result_data = {"input": input_data.content, "source": input_data.source.value}
        processing_result = ProcessingResult(
            success=True, output=result_data, metadata={"processed_at": "test_time"}
        )

        # Step 3: Format output as JSON
        formatted_output = self.output_formatter.format_output(
            processing_result.output, "json"
        )

        # Verify the output is valid JSON
        parsed = json.loads(formatted_output)
        assert parsed["input"] == "hello world"
        assert parsed["source"] == "args"

    def test_complete_workflow_file_to_table(self):
        """Test complete workflow from file input to table output."""
        # Create a temporary file with JSON data
        test_data = [
            {"name": "Alice", "age": 30, "city": "New York"},
            {"name": "Bob", "age": 25, "city": "London"},
        ]

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            json.dump(test_data, f)
            temp_path = f.name

        try:
            # Step 1: Read from file
            input_data = self.input_handler.read_from_file(temp_path)

            # Verify input data
            assert input_data.source == InputSource.FILE
            assert "file_path" in input_data.metadata

            # Step 2: Parse the JSON content
            parsed_data = json.loads(input_data.content)

            # Step 3: Format as table
            table_output = self.output_formatter.format_output(parsed_data, "table")

            # Verify table format
            assert "name" in table_output
            assert "age" in table_output
            assert "city" in table_output
            assert "Alice" in table_output
            assert "Bob" in table_output
            assert "|" in table_output  # Table separator

        finally:
            Path(temp_path).unlink()

    def test_error_handling_workflow(self):
        """Test error handling workflow."""
        # Try to read from non-existent file
        try:
            self.input_handler.read_from_file("non_existent_file.txt")
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError as e:
            # Handle the error using ErrorHandler
            error_result = self.error_handler.handle_file_error(
                e, "non_existent_file.txt"
            )

            # Verify error result structure
            assert isinstance(error_result, ProcessingResult)
            assert not error_result.success
            assert "File not found" in error_result.error_message
            assert "suggestions" in error_result.metadata
            assert len(error_result.metadata["suggestions"]) > 0

    def test_encoding_workflow(self):
        """Test encoding detection and validation workflow."""
        # Create file with UTF-8 content including non-ASCII characters
        content = "Hello, 世界! 🌍"

        with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as f:
            f.write(content)
            temp_path = f.name

        try:
            # Read file and verify encoding detection
            input_data = self.input_handler.read_from_file(temp_path)

            assert input_data.content == content
            assert "detected_encoding" in input_data.metadata

            # Verify encoding validation
            assert self.input_handler.validate_encoding(content, input_data.encoding)

        finally:
            Path(temp_path).unlink()

    def test_stdin_simulation_workflow(self):
        """Test stdin workflow with simulated input."""
        # Simulate stdin with StringIO
        test_input = "line1\nline2\nline3"
        mock_stdin = StringIO(test_input)
        mock_stdin.isatty = lambda: False  # Simulate non-TTY

        # Read from simulated stdin
        input_data = self.input_handler.read_from_stdin(mock_stdin)

        assert input_data.source == InputSource.STDIN
        assert input_data.content == test_input
        assert input_data.metadata["length"] == len(test_input)

        # Format the output
        formatted = self.output_formatter.format_output(input_data.content, "plain")
        assert formatted == test_input
