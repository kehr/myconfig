"""
Pytest configuration and shared fixtures for MyConfig tests.
"""
import pytest
import tempfile
import shutil
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.config import AppConfig, ConfigManager
from core.executor import CommandExecutor


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing."""
    return AppConfig(
        interactive=False,
        dry_run=True,
        verbose=False,
        quiet=True,
        enable_mas=False,
        enable_vscode=True,
        enable_defaults=True,
        enable_launchagents=True
    )


@pytest.fixture
def mock_executor(mock_config):
    """Create a mock command executor."""
    return CommandExecutor(mock_config)


@pytest.fixture
def sample_config_file(temp_dir):
    """Create a sample TOML config file."""
    config_content = """
[settings]
interactive = false
dry_run = true
verbose = false
quiet = true

[components]
enable_mas = false
enable_vscode = true
enable_defaults = true
enable_launchagents = true
"""
    config_path = os.path.join(temp_dir, "test_config.toml")
    with open(config_path, "w") as f:
        f.write(config_content)
    return config_path


@pytest.fixture
def mock_homebrew_output():
    """Mock Homebrew command output."""
    return {
        'list': 'git\nvim\ncurl\nwget',
        'list_cask': 'visual-studio-code\ngoogle-chrome\nfirefox',
        'tap': 'homebrew/core\nhomebrew/cask\nhomebrew/bundle'
    }


@pytest.fixture
def mock_vscode_output():
    """Mock VS Code extension list output."""
    return """ms-python.python
ms-vscode.cpptools
esbenp.prettier-vscode
ms-vscode.vscode-json"""


@pytest.fixture
def sample_dotfiles(temp_dir):
    """Create sample dotfiles for testing."""
    dotfiles = {
        '.zshrc': 'export PATH="/usr/local/bin:$PATH"',
        '.gitconfig': '[user]\n    name = Test User\n    email = test@example.com',
        '.vimrc': 'set number\nset autoindent'
    }
    
    created_files = {}
    for filename, content in dotfiles.items():
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        created_files[filename] = filepath
    
    return created_files


@pytest.fixture
def mock_defaults_output():
    """Mock macOS defaults command output."""
    return {
        'NSGlobalDomain': '{\n    AppleShowAllExtensions = 1;\n    AppleInterfaceStyle = Dark;\n}',
        'com.apple.finder': '{\n    ShowPathbar = 1;\n    AppleShowAllFiles = 1;\n}'
    }
