"""
Unit tests for command executor.
"""
import pytest
from unittest.mock import patch, MagicMock
import subprocess

from myconfig.core.executor import CommandExecutor
from myconfig.core.config import AppConfig


class TestCommandExecutor:
    """Test CommandExecutor class."""
    
    def test_init(self, mock_config):
        """Test executor initialization."""
        executor = CommandExecutor(mock_config)
        assert executor.config == mock_config
    
    @patch('subprocess.run')
    def test_run_command_success(self, mock_run, mock_config):
        """Test successful command execution."""
        mock_run.return_value = MagicMock(returncode=0, stdout="success")
        
        executor = CommandExecutor(mock_config)
        result = executor.run("echo test")
        
        assert result is True
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_run_command_failure(self, mock_run, mock_config):
        """Test failed command execution."""
        mock_run.return_value = MagicMock(returncode=1, stderr="error")
        
        executor = CommandExecutor(mock_config)
        result = executor.run("false")
        
        assert result is False
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_run_with_output(self, mock_run, mock_config):
        """Test command execution with output capture."""
        mock_run.return_value = MagicMock(returncode=0, stdout="test output")
        
        executor = CommandExecutor(mock_config)
        result = executor.run_output("echo test")
        
        assert result == "test output"
        mock_run.assert_called_once()
    
    @patch('subprocess.run')
    def test_run_output_failure(self, mock_run, mock_config):
        """Test command output capture on failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd", stderr="error")
        
        executor = CommandExecutor(mock_config)
        result = executor.run_output("false")
        
        assert result == ""
        mock_run.assert_called_once()
    
    def test_dry_run_mode(self, mock_config):
        """Test dry run mode doesn't execute commands."""
        config = mock_config.update(dry_run=True)
        executor = CommandExecutor(config)
        
        with patch('subprocess.run') as mock_run:
            result = executor.run("echo test")
            assert result is True
            mock_run.assert_not_called()
    
    @patch('builtins.input', return_value='y')
    @patch('subprocess.run')
    def test_interactive_confirmation_yes(self, mock_run, mock_input, mock_config):
        """Test interactive confirmation - yes."""
        config = mock_config.update(interactive=True, dry_run=False)
        mock_run.return_value = MagicMock(returncode=0)
        
        executor = CommandExecutor(config)
        result = executor.run("rm file", confirm=True)
        
        assert result is True
        mock_run.assert_called_once()
    
    @patch('builtins.input', return_value='n')
    @patch('subprocess.run')
    def test_interactive_confirmation_no(self, mock_run, mock_input, mock_config):
        """Test interactive confirmation - no."""
        config = mock_config.update(interactive=True, dry_run=False)
        
        executor = CommandExecutor(config)
        result = executor.run("rm file", confirm=True)
        
        assert result is True  # User declined, but not an error
        mock_run.assert_not_called()
    
    @patch('subprocess.run')
    def test_non_interactive_no_confirmation(self, mock_run, mock_config):
        """Test non-interactive mode skips confirmation."""
        config = mock_config.update(interactive=False, dry_run=False)
        mock_run.return_value = MagicMock(returncode=0)
        
        executor = CommandExecutor(config)
        result = executor.run("rm file", confirm=True)
        
        assert result is True
        mock_run.assert_called_once()
    
    def test_which_command_exists(self, mock_executor):
        """Test which() for existing command."""
        with patch('shutil.which', return_value='/usr/bin/git'):
            result = mock_executor.which('git')
            assert result == '/usr/bin/git'
    
    def test_which_command_missing(self, mock_executor):
        """Test which() for missing command."""
        with patch('shutil.which', return_value=None):
            result = mock_executor.which('nonexistent')
            assert result is None
