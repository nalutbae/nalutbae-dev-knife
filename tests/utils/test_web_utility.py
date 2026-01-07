"""
Unit tests for web development utilities.
"""

import pytest
from devknife.utils.web_utility import (
    GraphQLFormatter,
    CSSFormatter,
    CSSMinifier,
    URLExtractor,
)
from devknife.core.models import InputData, InputSource


class TestGraphQLFormatter:
    """Test cases for GraphQLFormatter utility."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = GraphQLFormatter()
    
    def test_graphql_formatting(self):
        """Test basic GraphQL query formatting."""
        input_data = InputData('query { user { name email } }', InputSource.ARGS)
        result = self.formatter.process(input_data, {})
        
        assert result.success
        assert 'query {' in result.output
        assert '  user {' in result.output
        assert '    name email' in result.output
        assert '  }' in result.output
        assert '}' in result.output
    
    def test_graphql_formatting_with_custom_indent(self):
        """Test GraphQL formatting with custom indentation."""
        input_data = InputData('query { user { name } }', InputSource.ARGS)
        result = self.formatter.process(input_data, {'indent': 4})
        
        assert result.success
        assert '    user {' in result.output
        assert result.metadata['indent'] == 4
    
    def test_mutation_formatting(self):
        """Test GraphQL mutation formatting."""
        input_data = InputData('mutation { createUser(input: { name: "John" }) { id } }', InputSource.ARGS)
        result = self.formatter.process(input_data, {})
        
        assert result.success
        assert 'mutation {' in result.output
        assert 'createUser' in result.output
    
    def test_empty_input(self):
        """Test handling of empty GraphQL input."""
        input_data = InputData('', InputSource.ARGS)
        result = self.formatter.process(input_data, {})
        
        assert not result.success
        assert 'Empty GraphQL query provided' in result.error_message
    
    def test_input_validation_valid(self):
        """Test input validation with valid GraphQL."""
        input_data = InputData('query { user }', InputSource.ARGS)
        assert self.formatter.validate_input(input_data)
    
    def test_input_validation_invalid(self):
        """Test input validation with invalid input."""
        input_data = InputData('not a graphql query', InputSource.ARGS)
        assert not self.formatter.validate_input(input_data)
    
    def test_command_info(self):
        """Test command information."""
        command = self.formatter.get_command_info()
        assert command.name == "graphql"
        assert command.category == "web"
        assert command.cli_enabled
        assert command.tui_enabled


class TestCSSFormatter:
    """Test cases for CSSFormatter utility."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = CSSFormatter()
    
    def test_css_formatting(self):
        """Test basic CSS formatting."""
        input_data = InputData('body{margin:0;padding:0}h1{color:red}', InputSource.ARGS)
        result = self.formatter.process(input_data, {})
        
        assert result.success
        # Check that the output contains properly formatted CSS
        assert 'body {' in result.output
        assert 'margin:0;' in result.output
        assert 'padding:0' in result.output
        assert 'h1 {' in result.output
        assert 'color:red' in result.output
    
    def test_css_formatting_with_custom_indent(self):
        """Test CSS formatting with custom indentation."""
        input_data = InputData('body{margin:0}', InputSource.ARGS)
        result = self.formatter.process(input_data, {'indent': 4})
        
        assert result.success
        assert '    margin:0' in result.output
        assert result.metadata['indent'] == 4
    
    def test_css_with_selectors(self):
        """Test CSS formatting with multiple selectors."""
        input_data = InputData('.container,.wrapper{width:100%}', InputSource.ARGS)
        result = self.formatter.process(input_data, {})
        
        assert result.success
        assert '.container,' in result.output
        assert '.wrapper {' in result.output
    
    def test_empty_input(self):
        """Test handling of empty CSS input."""
        input_data = InputData('', InputSource.ARGS)
        result = self.formatter.process(input_data, {})
        
        assert not result.success
        assert 'Empty CSS content provided' in result.error_message
    
    def test_input_validation_valid(self):
        """Test input validation with valid CSS."""
        input_data = InputData('body { margin: 0; }', InputSource.ARGS)
        assert self.formatter.validate_input(input_data)
    
    def test_input_validation_invalid(self):
        """Test input validation with invalid input."""
        input_data = InputData('not css content', InputSource.ARGS)
        assert not self.formatter.validate_input(input_data)
    
    def test_command_info(self):
        """Test command information."""
        command = self.formatter.get_command_info()
        assert command.name == "css"
        assert command.category == "web"
        assert command.cli_enabled
        assert command.tui_enabled


class TestCSSMinifier:
    """Test cases for CSSMinifier utility."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.minifier = CSSMinifier()
    
    def test_css_minification(self):
        """Test basic CSS minification."""
        input_data = InputData('body { margin: 0; padding: 0; }', InputSource.ARGS)
        result = self.minifier.process(input_data, {})
        
        assert result.success
        assert result.output == 'body{margin:0;padding:0}'
        assert 'compression_ratio' in result.metadata
    
    def test_css_minification_with_comments(self):
        """Test CSS minification with comments removal."""
        input_data = InputData('body { margin: 0; /* comment */ padding: 0; }', InputSource.ARGS)
        result = self.minifier.process(input_data, {})
        
        assert result.success
        assert '/* comment */' not in result.output
        assert result.output == 'body{margin:0;padding:0}'
    
    def test_css_minification_multiline_comments(self):
        """Test CSS minification with multiline comments."""
        css_input = '''body {
            margin: 0;
            /* This is a
               multiline comment */
            padding: 0;
        }'''
        input_data = InputData(css_input, InputSource.ARGS)
        result = self.minifier.process(input_data, {})
        
        assert result.success
        assert 'multiline comment' not in result.output
        assert result.output == 'body{margin:0;padding:0}'
    
    def test_css_minification_trailing_semicolon(self):
        """Test CSS minification removes trailing semicolons."""
        input_data = InputData('body { margin: 0; }', InputSource.ARGS)
        result = self.minifier.process(input_data, {})
        
        assert result.success
        assert result.output == 'body{margin:0}'
    
    def test_empty_input(self):
        """Test handling of empty CSS input."""
        input_data = InputData('', InputSource.ARGS)
        result = self.minifier.process(input_data, {})
        
        assert not result.success
        assert 'Empty CSS content provided' in result.error_message
    
    def test_input_validation_valid(self):
        """Test input validation with valid CSS."""
        input_data = InputData('body { margin: 0; }', InputSource.ARGS)
        assert self.minifier.validate_input(input_data)
    
    def test_input_validation_invalid(self):
        """Test input validation with invalid input."""
        input_data = InputData('not css content', InputSource.ARGS)
        assert not self.minifier.validate_input(input_data)
    
    def test_command_info(self):
        """Test command information."""
        command = self.minifier.get_command_info()
        assert command.name == "css-min"
        assert command.category == "web"
        assert command.cli_enabled
        assert command.tui_enabled


class TestURLExtractor:
    """Test cases for URLExtractor utility."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = URLExtractor()
    
    def test_url_extraction_href(self):
        """Test URL extraction from href attributes."""
        html = '<a href="https://example.com">Link</a>'
        input_data = InputData(html, InputSource.ARGS)
        result = self.extractor.process(input_data, {})
        
        assert result.success
        assert 'https://example.com' in result.output
        assert result.metadata['urls_found'] == 1
    
    def test_url_extraction_src(self):
        """Test URL extraction from src attributes."""
        html = '<img src="https://example.com/image.jpg">'
        input_data = InputData(html, InputSource.ARGS)
        result = self.extractor.process(input_data, {})
        
        assert result.success
        assert 'https://example.com/image.jpg' in result.output
    
    def test_url_extraction_multiple(self):
        """Test URL extraction from multiple sources."""
        html = '''
        <a href="https://example.com">Link</a>
        <img src="https://example.com/image.jpg">
        <form action="https://example.com/submit">
        '''
        input_data = InputData(html, InputSource.ARGS)
        result = self.extractor.process(input_data, {})
        
        assert result.success
        assert 'https://example.com' in result.output
        assert 'https://example.com/image.jpg' in result.output
        assert 'https://example.com/submit' in result.output
        assert result.metadata['urls_found'] == 3
    
    def test_url_extraction_with_base_url(self):
        """Test URL extraction with base URL for relative URLs."""
        html = '<a href="/page">Link</a><img src="/image.jpg">'
        input_data = InputData(html, InputSource.ARGS)
        result = self.extractor.process(input_data, {'base_url': 'https://example.com'})
        
        assert result.success
        assert 'https://example.com/page' in result.output
        assert 'https://example.com/image.jpg' in result.output
    
    def test_url_extraction_css_urls(self):
        """Test URL extraction from CSS url() functions."""
        html = '<style>body { background: url("https://example.com/bg.jpg"); }</style>'
        input_data = InputData(html, InputSource.ARGS)
        result = self.extractor.process(input_data, {})
        
        assert result.success
        assert 'https://example.com/bg.jpg' in result.output
    
    def test_url_extraction_plain_urls(self):
        """Test URL extraction from plain text URLs."""
        html = 'Visit https://example.com for more info'
        input_data = InputData(html, InputSource.ARGS)
        result = self.extractor.process(input_data, {})
        
        assert result.success
        assert 'https://example.com' in result.output
    
    def test_url_extraction_skip_fragments(self):
        """Test that fragment-only URLs are skipped."""
        html = '<a href="#section">Section</a>'
        input_data = InputData(html, InputSource.ARGS)
        result = self.extractor.process(input_data, {})
        
        assert result.success
        assert 'No URLs found' in result.output
    
    def test_url_extraction_skip_javascript(self):
        """Test that javascript: URLs are skipped."""
        html = '<a href="javascript:void(0)">Click</a>'
        input_data = InputData(html, InputSource.ARGS)
        result = self.extractor.process(input_data, {})
        
        assert result.success
        assert 'No URLs found' in result.output
    
    def test_url_extraction_skip_mailto(self):
        """Test that mailto: URLs are skipped."""
        html = '<a href="mailto:test@example.com">Email</a>'
        input_data = InputData(html, InputSource.ARGS)
        result = self.extractor.process(input_data, {})
        
        assert result.success
        assert 'No URLs found' in result.output
    
    def test_url_extraction_duplicates(self):
        """Test URL extraction with duplicate URLs."""
        html = '''
        <a href="https://example.com">Link1</a>
        <a href="https://example.com">Link2</a>
        '''
        input_data = InputData(html, InputSource.ARGS)
        result = self.extractor.process(input_data, {'unique': True})
        
        assert result.success
        assert result.metadata['urls_found'] == 1
        
        # Test with duplicates allowed
        result = self.extractor.process(input_data, {'unique': False})
        assert result.success
        assert result.metadata['urls_found'] == 2
    
    def test_empty_input(self):
        """Test handling of empty HTML input."""
        input_data = InputData('', InputSource.ARGS)
        result = self.extractor.process(input_data, {})
        
        assert not result.success
        assert 'Empty HTML content provided' in result.error_message
    
    def test_no_urls_found(self):
        """Test handling when no URLs are found."""
        input_data = InputData('<p>Just some text</p>', InputSource.ARGS)
        result = self.extractor.process(input_data, {})
        
        assert result.success
        assert 'No URLs found' in result.output
        assert result.metadata['urls_found'] == 0
    
    def test_input_validation_valid(self):
        """Test input validation with valid HTML."""
        input_data = InputData('<a href="test">Link</a>', InputSource.ARGS)
        assert self.extractor.validate_input(input_data)
    
    def test_input_validation_empty(self):
        """Test input validation with empty input."""
        input_data = InputData('', InputSource.ARGS)
        assert not self.extractor.validate_input(input_data)
    
    def test_command_info(self):
        """Test command information."""
        command = self.extractor.get_command_info()
        assert command.name == "url-extract"
        assert command.category == "web"
        assert command.cli_enabled
        assert command.tui_enabled