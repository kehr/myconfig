"""
Unit tests for backup components.
"""
import pytest
from unittest.mock import patch, MagicMock, mock_open
import os

from myconfig.core.components.homebrew import HomebrewComponent
from myconfig.core.components.vscode import VSCodeComponent
from myconfig.core.components.dotfiles import DotfilesComponent
from myconfig.core.components.defaults import DefaultsComponent


class TestHomebrewComponent:
    """Test Homebrew backup component."""
    
    def test_init(self, mock_executor):
        """Test component initialization."""
        component = HomebrewComponent(mock_executor)
        assert component.name == "Homebrew"
        assert component.executor == mock_executor
    
    def test_is_available_with_homebrew(self, mock_executor):
        """Test availability check when Homebrew is installed."""
        mock_executor.which = MagicMock(return_value='/usr/local/bin/brew')
        component = HomebrewComponent(mock_executor)
        assert component.is_available() is True
    
    def test_is_available_without_homebrew(self, mock_executor):
        """Test availability check when Homebrew is not installed."""
        mock_executor.which = MagicMock(return_value=None)
        component = HomebrewComponent(mock_executor)
        assert component.is_available() is False
    
    @patch('builtins.open', mock_open())
    def test_export_success(self, mock_executor, temp_dir):
        """Test successful Homebrew export."""
        mock_executor.which = MagicMock(return_value='/usr/local/bin/brew')
        mock_executor.run_output = MagicMock(side_effect=[
            'git\nvim\ncurl',  # brew list
            'visual-studio-code\ngoogle-chrome',  # brew list --cask
            'homebrew/core\nhomebrew/cask'  # brew tap
        ])
        
        component = HomebrewComponent(mock_executor)
        result = component.export(temp_dir)
        
        assert result is True
        assert mock_executor.run_output.call_count == 3
    
    def test_export_unavailable(self, mock_executor, temp_dir):
        """Test export when Homebrew is unavailable."""
        mock_executor.which = MagicMock(return_value=None)
        component = HomebrewComponent(mock_executor)
        result = component.export(temp_dir)
        assert result is False
    
    def test_preview(self, mock_executor):
        """Test preview functionality."""
        mock_executor.which = MagicMock(return_value='/usr/local/bin/brew')
        mock_executor.run_output = MagicMock(side_effect=[
            'git\nvim',
            'vscode\nchrome',
            'homebrew/core'
        ])
        
        component = HomebrewComponent(mock_executor)
        info = component.preview()
        
        assert 'formulae' in info
        assert 'casks' in info
        assert 'taps' in info
        assert info['formulae'] == 2
        assert info['casks'] == 2


class TestVSCodeComponent:
    """Test VS Code backup component."""
    
    def test_is_available_with_code(self, mock_executor):
        """Test availability when code command exists."""
        mock_executor.which = MagicMock(return_value='/usr/local/bin/code')
        component = VSCodeComponent(mock_executor)
        assert component.is_available() is True
    
    def test_is_available_without_code(self, mock_executor):
        """Test availability when code command missing."""
        mock_executor.which = MagicMock(return_value=None)
        component = VSCodeComponent(mock_executor)
        assert component.is_available() is False
    
    @patch('builtins.open', mock_open())
    def test_export_extensions(self, mock_executor, temp_dir):
        """Test VS Code extension export."""
        mock_executor.which = MagicMock(return_value='/usr/local/bin/code')
        mock_executor.run_output = MagicMock(return_value='ms-python.python\nms-vscode.cpptools')
        
        component = VSCodeComponent(mock_executor)
        result = component.export(temp_dir)
        
        assert result is True
        mock_executor.run_output.assert_called_once()
    
    def test_preview_extensions(self, mock_executor):
        """Test VS Code extension preview."""
        mock_executor.which = MagicMock(return_value='/usr/local/bin/code')
        mock_executor.run_output = MagicMock(return_value='ext1\next2\next3')
        
        component = VSCodeComponent(mock_executor)
        info = component.preview()
        
        assert info['extensions'] == 3


class TestDotfilesComponent:
    """Test dotfiles backup component."""
    
    def test_init(self, mock_executor):
        """Test dotfiles component initialization."""
        component = DotfilesComponent(mock_executor)
        assert component.name == "Dotfiles"
    
    def test_is_available(self, mock_executor):
        """Test dotfiles component is always available."""
        component = DotfilesComponent(mock_executor)
        assert component.is_available() is True
    
    @patch('os.path.exists')
    @patch('shutil.copy2')
    @patch('os.makedirs')
    def test_export_dotfiles(self, mock_makedirs, mock_copy, mock_exists, mock_executor, temp_dir):
        """Test dotfiles export."""
        mock_exists.return_value = True
        
        component = DotfilesComponent(mock_executor)
        result = component.export(temp_dir)
        
        assert result is True
        # Should attempt to copy files
        assert mock_copy.called
    
    @patch('os.path.exists')
    def test_preview_dotfiles(self, mock_exists, mock_executor):
        """Test dotfiles preview."""
        # Mock some files exist, some don't
        def exists_side_effect(path):
            return path.endswith(('.zshrc', '.gitconfig'))
        
        mock_exists.side_effect = exists_side_effect
        
        component = DotfilesComponent(mock_executor)
        info = component.preview()
        
        assert 'files_found' in info
        assert info['files_found'] >= 0


class TestDefaultsComponent:
    """Test system defaults backup component."""
    
    def test_is_available(self, mock_executor):
        """Test defaults component availability."""
        mock_executor.which = MagicMock(return_value='/usr/bin/defaults')
        component = DefaultsComponent(mock_executor)
        assert component.is_available() is True
    
    @patch('builtins.open', mock_open())
    def test_export_defaults(self, mock_executor, temp_dir):
        """Test system defaults export."""
        mock_executor.which = MagicMock(return_value='/usr/bin/defaults')
        mock_executor.run_output = MagicMock(return_value='{\n    key = value;\n}')
        
        component = DefaultsComponent(mock_executor)
        result = component.export(temp_dir)
        
        assert result is True
    
    def test_preview_defaults(self, mock_executor):
        """Test defaults preview."""
        mock_executor.which = MagicMock(return_value='/usr/bin/defaults')
        
        component = DefaultsComponent(mock_executor)
        info = component.preview()
        
        assert 'domains' in info
        assert isinstance(info['domains'], int)
