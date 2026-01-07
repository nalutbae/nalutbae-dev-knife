"""
Integration tests for CLI and TUI interface integration.
"""

import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from devknife.core.config_manager import ConfigManager
from devknife.core.error_handling import get_cli_error_handler, get_tui_error_handler
from devknife.main import detect_interface_preference, setup_environment


class TestInterfaceIntegration:
    """Test CLI and TUI interface integration."""
    
    def test_detect_interface_preference_tui_flag(self):
        """Test interface detection with TUI flag."""
        args = ['devknife', '--tui']
        result = detect_interface_preference(args)
        assert result == 'tui'
    
    def test_detect_interface_preference_cli_flag(self):
        """Test interface detection with CLI flag."""
        args = ['devknife', '--cli']
        result = detect_interface_preference(args)
        assert result == 'cli'
    
    def test_detect_interface_preference_with_command(self):
        """Test interface detection with command arguments."""
        args = ['devknife', 'base64', 'hello']
        result = detect_interface_preference(args)
        assert result == 'cli'
    
    def test_detect_interface_preference_no_args(self):
        """Test interface detection with no arguments."""
        args = ['devknife']
        result = detect_interface_preference(args)
        assert result == 'tui'  # Default to TUI
    
    def test_setup_environment(self):
        """Test environment setup."""
        # This should not raise any exceptions
        setup_environment()


class TestConfigurationIntegration:
    """Test configuration system integration."""
    
    def test_config_manager_creation(self):
        """Test configuration manager creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            manager = ConfigManager(config_dir)
            
            # Load default config
            config = manager.load_config()
            assert config.default_interface == 'tui'
            assert config.default_encoding == 'utf-8'
    
    def test_config_persistence(self):
        """Test configuration persistence."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            
            # Create and update config
            manager = ConfigManager(config_dir)
            manager.update_config(default_interface='cli', tui_theme='dark')
            
            # Create new manager and verify persistence
            new_manager = ConfigManager(config_dir)
            config = new_manager.load_config()
            
            assert config.default_interface == 'cli'
            assert config.tui_theme == 'dark'
    
    def test_config_preferences(self):
        """Test configuration preferences."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            manager = ConfigManager(config_dir)
            
            # Set and get preferences
            manager.set_preference('default_interface', 'cli')
            interface = manager.get_preference('default_interface')
            
            assert interface == 'cli'
            
            # Test default value
            unknown = manager.get_preference('unknown_key', 'default_value')
            assert unknown == 'default_value'


class TestErrorHandlingIntegration:
    """Test unified error handling integration."""
    
    def test_cli_error_handler(self):
        """Test CLI error handler."""
        handler = get_cli_error_handler()
        test_error = ValueError("Test error")
        
        result = handler.handle_exception(test_error)
        
        assert not result.success
        assert result.error_message is not None
        assert 'Test error' in result.error_message
        assert result.metadata is not None
        assert result.metadata['error_type'] == 'ValueError'
    
    def test_tui_error_handler(self):
        """Test TUI error handler."""
        handler = get_tui_error_handler()
        test_error = FileNotFoundError("File not found")
        
        error_info = handler.handle_for_notification(test_error)
        
        assert 'title' in error_info
        assert 'message' in error_info
        assert 'suggestions' in error_info
        assert 'severity' in error_info
        assert len(error_info['suggestions']) > 0
    
    def test_error_message_formatting(self):
        """Test error message formatting for different interfaces."""
        cli_handler = get_cli_error_handler()
        tui_handler = get_tui_error_handler()
        
        test_error = PermissionError("Permission denied")
        
        # Test CLI formatting
        cli_result = cli_handler.handle_exception(test_error)
        cli_message = cli_handler.format_error_for_cli(cli_result)
        
        assert '오류:' in cli_message
        assert '제안사항:' in cli_message
        
        # Test TUI formatting
        tui_info = tui_handler.handle_for_notification(test_error)
        
        assert tui_info['title'] == '오류 발생'
        assert '권한' in tui_info['message']
        assert len(tui_info['suggestions']) > 0
    
    def test_error_suggestions_generation(self):
        """Test error suggestions generation."""
        handler = get_cli_error_handler()
        
        # Test different error types
        errors_and_expected_suggestions = [
            (FileNotFoundError("test.txt"), "파일 경로가 올바른지 확인하세요"),
            (PermissionError("access denied"), "파일 권한을 확인하세요"),
            (UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid'), "파일 인코딩을 확인하세요"),
            (ValueError("invalid input"), "입력 형식을 확인하세요"),
            (ImportError("module not found"), "필요한 패키지가 설치되어 있는지 확인하세요"),
        ]
        
        for error, expected_suggestion in errors_and_expected_suggestions:
            result = handler.handle_exception(error)
            suggestions = result.metadata.get('suggestions', [])
            
            assert len(suggestions) > 0
            assert any(expected_suggestion in suggestion for suggestion in suggestions)


class TestSharedUtilityModules:
    """Test that CLI and TUI use the same utility modules."""
    
    def test_shared_registry(self):
        """Test that both interfaces use the same command registry."""
        from devknife.core.router import get_global_registry
        
        # Get registry instances
        registry1 = get_global_registry()
        registry2 = get_global_registry()
        
        # Should be the same instance
        assert registry1 is registry2
    
    def test_shared_router(self):
        """Test that both interfaces use the same command router."""
        from devknife.core.router import get_global_router
        
        # Get router instances
        router1 = get_global_router()
        router2 = get_global_router()
        
        # Should be the same instance
        assert router1 is router2
    
    @patch('devknife.cli.main.setup_utilities')
    def test_cli_utility_setup(self, mock_setup):
        """Test that CLI sets up utilities."""
        from devknife.cli.main import main
        from click.testing import CliRunner
        
        runner = CliRunner()
        # Use a command that actually invokes the main function
        result = runner.invoke(main, ['list'])
        
        # Should call setup_utilities
        mock_setup.assert_called_once()
    
    def test_utility_registration_consistency(self):
        """Test that utility registration is consistent."""
        from devknife.core.router import get_global_registry
        from devknife.cli.main import setup_utilities
        
        # Setup utilities
        setup_utilities()
        
        registry = get_global_registry()
        commands = registry.list_commands()
        
        # Should have registered commands
        assert len(commands) > 0
        
        # Check some expected commands
        expected_commands = ['base64', 'json', 'csv2md', 'uuid-gen', 'hash']
        for cmd in expected_commands:
            assert cmd in commands