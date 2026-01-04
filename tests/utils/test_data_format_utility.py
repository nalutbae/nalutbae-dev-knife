"""
Unit tests for data format utility modules.
"""

import json
import pytest
from devknife.utils.data_format_utility import (
    JSONFormatter,
    JSONToYAMLConverter,
    XMLFormatter,
    JSONToPythonClassGenerator,
    CSVToMarkdownConverter,
    TSVToMarkdownConverter,
    CSVToJSONConverter,
)
from devknife.core.models import InputData, InputSource


class TestJSONFormatter:
    """Test cases for JSONFormatter utility."""
    
    def test_json_formatting(self):
        """Test basic JSON formatting."""
        formatter = JSONFormatter()
        input_data = InputData('{"name":"John","age":30}', InputSource.ARGS)
        result = formatter.process(input_data, {})
        
        assert result.success
        assert '"name": "John"' in result.output
        assert '"age": 30' in result.output
        assert result.metadata['operation'] == 'format'
    
    def test_json_formatting_with_custom_indent(self):
        """Test JSON formatting with custom indentation."""
        formatter = JSONFormatter()
        input_data = InputData('{"name":"John","age":30}', InputSource.ARGS)
        result = formatter.process(input_data, {'indent': 4})
        
        assert result.success
        assert '    "name": "John"' in result.output
        assert result.metadata['indent'] == 4
    
    def test_json_recovery_trailing_comma(self):
        """Test JSON recovery with trailing comma."""
        formatter = JSONFormatter()
        input_data = InputData('{"name":"John","age":30,}', InputSource.ARGS)
        result = formatter.process(input_data, {'recover': True})
        
        assert result.success
        assert '"name": "John"' in result.output
        assert '"age": 30' in result.output
        assert 'removed trailing commas' in result.warnings[0]
    
    def test_json_recovery_single_quotes(self):
        """Test JSON recovery with single quotes."""
        formatter = JSONFormatter()
        input_data = InputData("{'name':'John','age':30}", InputSource.ARGS)
        result = formatter.process(input_data, {'recover': True})
        
        assert result.success
        assert '"name": "John"' in result.output
        assert '"age": 30' in result.output
    
    def test_invalid_json_without_recovery(self):
        """Test invalid JSON without recovery mode."""
        formatter = JSONFormatter()
        input_data = InputData('{"name":"John","age":30,}', InputSource.ARGS)
        result = formatter.process(input_data, {})
        
        assert not result.success
        assert "Invalid JSON format" in result.error_message
        assert "--recover" in result.error_message
    
    def test_unrecoverable_json(self):
        """Test JSON that cannot be recovered."""
        formatter = JSONFormatter()
        input_data = InputData('{"name":John,age:}', InputSource.ARGS)
        result = formatter.process(input_data, {'recover': True})
        
        assert not result.success
        assert "Could not recover JSON" in result.error_message
    
    def test_command_info(self):
        """Test command information."""
        formatter = JSONFormatter()
        cmd_info = formatter.get_command_info()
        
        assert cmd_info.name == "json"
        assert cmd_info.category == "data_format"
        assert cmd_info.cli_enabled
        assert cmd_info.tui_enabled
    
    def test_input_validation(self):
        """Test input validation."""
        formatter = JSONFormatter()
        
        valid_input = InputData('{"test": "value"}', InputSource.ARGS)
        assert formatter.validate_input(valid_input)
        
        empty_input = InputData('', InputSource.ARGS)
        assert not formatter.validate_input(empty_input)


class TestJSONToYAMLConverter:
    """Test cases for JSONToYAMLConverter utility."""
    
    def test_json_to_yaml_conversion(self):
        """Test basic JSON to YAML conversion."""
        converter = JSONToYAMLConverter()
        input_data = InputData('{"name":"John","age":30,"hobbies":["reading","coding"]}', InputSource.ARGS)
        result = converter.process(input_data, {})
        
        assert result.success
        assert 'name: John' in result.output
        assert 'age: 30' in result.output
        assert '- reading' in result.output
        assert '- coding' in result.output
    
    def test_nested_json_to_yaml(self):
        """Test nested JSON to YAML conversion."""
        converter = JSONToYAMLConverter()
        input_data = InputData('{"person":{"name":"John","details":{"age":30}}}', InputSource.ARGS)
        result = converter.process(input_data, {})
        
        assert result.success
        assert 'person:' in result.output
        assert 'name: John' in result.output
        assert 'details:' in result.output
        assert 'age: 30' in result.output
    
    def test_invalid_json_input(self):
        """Test invalid JSON input."""
        converter = JSONToYAMLConverter()
        input_data = InputData('{"name":"John",}', InputSource.ARGS)
        result = converter.process(input_data, {})
        
        assert not result.success
        assert "Invalid JSON input" in result.error_message
    
    def test_input_validation(self):
        """Test input validation."""
        converter = JSONToYAMLConverter()
        
        valid_input = InputData('{"test": "value"}', InputSource.ARGS)
        assert converter.validate_input(valid_input)
        
        invalid_input = InputData('{"test": "value",}', InputSource.ARGS)
        assert not converter.validate_input(invalid_input)
        
        empty_input = InputData('', InputSource.ARGS)
        assert not converter.validate_input(empty_input)


class TestXMLFormatter:
    """Test cases for XMLFormatter utility."""
    
    def test_xml_formatting(self):
        """Test basic XML formatting."""
        formatter = XMLFormatter()
        input_data = InputData('<root><person><name>John</name><age>30</age></person></root>', InputSource.ARGS)
        result = formatter.process(input_data, {})
        
        assert result.success
        assert '<root>' in result.output
        assert '<person>' in result.output
        assert '<name>John</name>' in result.output
        assert '<age>30</age>' in result.output
    
    def test_xml_formatting_with_custom_indent(self):
        """Test XML formatting with custom indentation."""
        formatter = XMLFormatter()
        input_data = InputData('<root><item>value</item></root>', InputSource.ARGS)
        result = formatter.process(input_data, {'indent': 4})
        
        assert result.success
        assert result.metadata['indent'] == 4
    
    def test_invalid_xml_input(self):
        """Test invalid XML input."""
        formatter = XMLFormatter()
        input_data = InputData('<root><unclosed>', InputSource.ARGS)
        result = formatter.process(input_data, {})
        
        assert not result.success
        assert "Invalid XML format" in result.error_message
    
    def test_input_validation(self):
        """Test input validation."""
        formatter = XMLFormatter()
        
        valid_input = InputData('<root><item>test</item></root>', InputSource.ARGS)
        assert formatter.validate_input(valid_input)
        
        invalid_input = InputData('<root><unclosed>', InputSource.ARGS)
        assert not formatter.validate_input(invalid_input)
        
        empty_input = InputData('', InputSource.ARGS)
        assert not formatter.validate_input(empty_input)


class TestJSONToPythonClassGenerator:
    """Test cases for JSONToPythonClassGenerator utility."""
    
    def test_simple_json_to_class(self):
        """Test simple JSON to Python class generation."""
        generator = JSONToPythonClassGenerator()
        input_data = InputData('{"name":"John","age":30,"active":true}', InputSource.ARGS)
        result = generator.process(input_data, {'class_name': 'Person'})
        
        assert result.success
        assert '@dataclass' in result.output
        assert 'class Person:' in result.output
        assert 'name: str' in result.output
        assert 'age: int' in result.output
        assert 'active: bool' in result.output
    
    def test_nested_json_to_class(self):
        """Test nested JSON to Python class generation."""
        generator = JSONToPythonClassGenerator()
        input_data = InputData('{"name":"John","hobbies":["reading","coding"],"details":{"age":30}}', InputSource.ARGS)
        result = generator.process(input_data, {'class_name': 'Person'})
        
        assert result.success
        assert 'name: str' in result.output
        assert 'hobbies: List[str]' in result.output
        assert 'details: Dict[str, Any]' in result.output
    
    def test_default_class_name(self):
        """Test default class name generation."""
        generator = JSONToPythonClassGenerator()
        input_data = InputData('{"test":"value"}', InputSource.ARGS)
        result = generator.process(input_data, {})
        
        assert result.success
        assert 'class GeneratedClass:' in result.output
    
    def test_invalid_json_input(self):
        """Test invalid JSON input."""
        generator = JSONToPythonClassGenerator()
        input_data = InputData('{"name":"John",}', InputSource.ARGS)
        result = generator.process(input_data, {})
        
        assert not result.success
        assert "Invalid JSON input" in result.error_message
    
    def test_safe_identifier_conversion(self):
        """Test safe identifier conversion for invalid Python names."""
        generator = JSONToPythonClassGenerator()
        input_data = InputData('{"class":"value","123field":"test","with-dash":"data"}', InputSource.ARGS)
        result = generator.process(input_data, {'class_name': 'TestClass'})
        
        assert result.success
        assert 'class_field: str' in result.output  # Python keyword
        assert 'field_123field: str' in result.output  # Starts with number
        assert 'with_dash: str' in result.output  # Contains dash
    
    def test_input_validation(self):
        """Test input validation."""
        generator = JSONToPythonClassGenerator()
        
        valid_input = InputData('{"test": "value"}', InputSource.ARGS)
        assert generator.validate_input(valid_input)
        
        invalid_input = InputData('{"test": "value",}', InputSource.ARGS)
        assert not generator.validate_input(invalid_input)
        
        empty_input = InputData('', InputSource.ARGS)
        assert not generator.validate_input(empty_input)


class TestCSVToMarkdownConverter:
    """Test cases for CSVToMarkdownConverter utility."""
    
    def test_csv_to_markdown_with_header(self):
        """Test CSV to Markdown conversion with header."""
        converter = CSVToMarkdownConverter()
        input_data = InputData('name,age,city\nJohn,30,NYC\nJane,25,LA', InputSource.ARGS)
        result = converter.process(input_data, {})
        
        assert result.success
        assert '| name | age | city |' in result.output
        assert '| --- | --- | --- |' in result.output
        assert '| John | 30 | NYC |' in result.output
        assert '| Jane | 25 | LA |' in result.output
        assert result.metadata['operation'] == 'csv_to_markdown'
        assert result.metadata['rows_processed'] == 3
        assert result.metadata['has_header'] == True
    
    def test_csv_to_markdown_without_header(self):
        """Test CSV to Markdown conversion without header."""
        converter = CSVToMarkdownConverter()
        input_data = InputData('apple,red\nbanana,yellow', InputSource.ARGS)
        result = converter.process(input_data, {'has_header': False})
        
        assert result.success
        assert '| apple | red |' in result.output
        assert '| banana | yellow |' in result.output
        # Should not have separator row when no header
        assert '| --- | --- |' not in result.output
        assert result.metadata['has_header'] == False
    
    def test_csv_with_pipe_characters(self):
        """Test CSV with pipe characters that need escaping."""
        converter = CSVToMarkdownConverter()
        input_data = InputData('name,description\nJohn,likes | pipes\nJane,normal text', InputSource.ARGS)
        result = converter.process(input_data, {})
        
        assert result.success
        assert '| likes \\| pipes |' in result.output
        assert '| normal text |' in result.output
    
    def test_csv_with_uneven_columns(self):
        """Test CSV with uneven column counts."""
        converter = CSVToMarkdownConverter()
        input_data = InputData('name,age\nJohn,30,extra\nJane', InputSource.ARGS)
        result = converter.process(input_data, {})
        
        assert result.success
        # Should pad missing columns
        assert '| name | age |  |' in result.output
        assert '| John | 30 | extra |' in result.output
        assert '| Jane |  |  |' in result.output
    
    def test_empty_csv_input(self):
        """Test empty CSV input."""
        converter = CSVToMarkdownConverter()
        input_data = InputData('', InputSource.ARGS)
        result = converter.process(input_data, {})
        
        assert not result.success
        assert "Empty CSV input provided" in result.error_message
    
    def test_input_validation(self):
        """Test input validation."""
        converter = CSVToMarkdownConverter()
        
        valid_input = InputData('name,age\nJohn,30', InputSource.ARGS)
        assert converter.validate_input(valid_input)
        
        empty_input = InputData('', InputSource.ARGS)
        assert not converter.validate_input(empty_input)


class TestTSVToMarkdownConverter:
    """Test cases for TSVToMarkdownConverter utility."""
    
    def test_tsv_to_markdown_with_header(self):
        """Test TSV to Markdown conversion with header."""
        converter = TSVToMarkdownConverter()
        input_data = InputData('name\tage\tcity\nJohn\t30\tNYC\nJane\t25\tLA', InputSource.ARGS)
        result = converter.process(input_data, {})
        
        assert result.success
        assert '| name | age | city |' in result.output
        assert '| --- | --- | --- |' in result.output
        assert '| John | 30 | NYC |' in result.output
        assert '| Jane | 25 | LA |' in result.output
        assert result.metadata['operation'] == 'tsv_to_markdown'
        assert result.metadata['rows_processed'] == 3
        assert result.metadata['has_header'] == True
    
    def test_tsv_to_markdown_without_header(self):
        """Test TSV to Markdown conversion without header."""
        converter = TSVToMarkdownConverter()
        input_data = InputData('apple\tred\nbanana\tyellow', InputSource.ARGS)
        result = converter.process(input_data, {'has_header': False})
        
        assert result.success
        assert '| apple | red |' in result.output
        assert '| banana | yellow |' in result.output
        # Should not have separator row when no header
        assert '| --- | --- |' not in result.output
        assert result.metadata['has_header'] == False
    
    def test_tsv_with_pipe_characters(self):
        """Test TSV with pipe characters that need escaping."""
        converter = TSVToMarkdownConverter()
        input_data = InputData('name\tdescription\nJohn\tlikes | pipes\nJane\tnormal text', InputSource.ARGS)
        result = converter.process(input_data, {})
        
        assert result.success
        assert '| likes \\| pipes |' in result.output
        assert '| normal text |' in result.output
    
    def test_empty_tsv_input(self):
        """Test empty TSV input."""
        converter = TSVToMarkdownConverter()
        input_data = InputData('', InputSource.ARGS)
        result = converter.process(input_data, {})
        
        assert not result.success
        assert "Empty TSV input provided" in result.error_message
    
    def test_input_validation(self):
        """Test input validation."""
        converter = TSVToMarkdownConverter()
        
        valid_input = InputData('name\tage\nJohn\t30', InputSource.ARGS)
        assert converter.validate_input(valid_input)
        
        empty_input = InputData('', InputSource.ARGS)
        assert not converter.validate_input(empty_input)


class TestCSVToJSONConverter:
    """Test cases for CSVToJSONConverter utility."""
    
    def test_csv_to_json_with_header(self):
        """Test CSV to JSON conversion with header."""
        converter = CSVToJSONConverter()
        input_data = InputData('name,age,active\nJohn,30,true\nJane,25,false', InputSource.ARGS)
        result = converter.process(input_data, {})
        
        assert result.success
        json_data = json.loads(result.output)
        assert len(json_data) == 2
        assert json_data[0]['name'] == 'John'
        assert json_data[0]['age'] == 30  # Should be converted to int
        assert json_data[0]['active'] == True  # Should be converted to bool
        assert json_data[1]['name'] == 'Jane'
        assert json_data[1]['age'] == 25
        assert json_data[1]['active'] == False
        assert result.metadata['operation'] == 'csv_to_json'
        assert result.metadata['has_header'] == True
    
    def test_csv_to_json_without_header(self):
        """Test CSV to JSON conversion without header."""
        converter = CSVToJSONConverter()
        input_data = InputData('apple,red\nbanana,yellow', InputSource.ARGS)
        result = converter.process(input_data, {'has_header': False})
        
        assert result.success
        json_data = json.loads(result.output)
        assert json_data == [['apple', 'red'], ['banana', 'yellow']]
        assert result.metadata['has_header'] == False
    
    def test_csv_to_json_with_numeric_conversion(self):
        """Test CSV to JSON with numeric value conversion."""
        converter = CSVToJSONConverter()
        input_data = InputData('name,age,score,active\nJohn,30,95.5,true\nJane,25,87.2,false', InputSource.ARGS)
        result = converter.process(input_data, {})
        
        assert result.success
        json_data = json.loads(result.output)
        assert json_data[0]['age'] == 30  # int
        assert json_data[0]['score'] == 95.5  # float
        assert json_data[0]['active'] == True  # bool
        assert json_data[1]['age'] == 25
        assert json_data[1]['score'] == 87.2
        assert json_data[1]['active'] == False
    
    def test_csv_to_json_with_custom_indent(self):
        """Test CSV to JSON with custom indentation."""
        converter = CSVToJSONConverter()
        input_data = InputData('name,age\nJohn,30', InputSource.ARGS)
        result = converter.process(input_data, {'indent': 4})
        
        assert result.success
        assert '    "name": "John"' in result.output
        assert result.metadata['indent'] == 4
    
    def test_csv_to_json_with_uneven_columns(self):
        """Test CSV to JSON with uneven column counts."""
        converter = CSVToJSONConverter()
        input_data = InputData('name,age,city\nJohn,30\nJane,25,LA,extra', InputSource.ARGS)
        result = converter.process(input_data, {})
        
        assert result.success
        json_data = json.loads(result.output)
        assert json_data[0]['city'] == ''  # Missing value should be empty string
        assert len(json_data[1]) == 3  # Extra values should be ignored for object keys
    
    def test_empty_csv_input(self):
        """Test empty CSV input."""
        converter = CSVToJSONConverter()
        input_data = InputData('', InputSource.ARGS)
        result = converter.process(input_data, {})
        
        assert not result.success
        assert "Empty CSV input provided" in result.error_message
    
    def test_input_validation(self):
        """Test input validation."""
        converter = CSVToJSONConverter()
        
        valid_input = InputData('name,age\nJohn,30', InputSource.ARGS)
        assert converter.validate_input(valid_input)
        
        empty_input = InputData('', InputSource.ARGS)
        assert not converter.validate_input(empty_input)